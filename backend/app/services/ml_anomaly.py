import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import IsolationForest
import warnings

warnings.filterwarnings('ignore')

# ----------------- DAGMM PyTorch Implementation ----------------- #
class CompressionNet(nn.Module):
    def __init__(self, in_dim, latent_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_dim, 16),
            nn.Tanh(),
            nn.Linear(16, 8),
            nn.Tanh(),
            nn.Linear(8, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 8),
            nn.Tanh(),
            nn.Linear(8, 16),
            nn.Tanh(),
            nn.Linear(16, in_dim)
        )
        
    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return z, x_hat

class EstimationNet(nn.Module):
    def __init__(self, z_dim, n_gmm):
        # Input to estimation network is [z, cosine_dist, euclidean_dist] -> dim = z_dim + 2
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim + 2, 10),
            nn.Tanh(),
            nn.Dropout(0.5),
            nn.Linear(10, n_gmm),
            nn.Softmax(dim=1)
        )
        
    def forward(self, z):
        return self.net(z)

class DAGMM(nn.Module):
    def __init__(self, in_dim=5, latent_dim=1, n_gmm=2):
        super().__init__()
        self.comp = CompressionNet(in_dim, latent_dim)
        self.est = EstimationNet(latent_dim, n_gmm)
        
        # GMM parameters stored as buffers so they don't get updated by optimizer
        self.register_buffer("phi", torch.zeros(n_gmm))
        self.register_buffer("mu", torch.zeros(n_gmm, latent_dim + 2))
        self.register_buffer("cov", torch.zeros(n_gmm, latent_dim + 2, latent_dim + 2))
        
    def forward(self, x):
        z, x_hat = self.comp(x)
        
        # Calculate reconstruction errors
        cos_dist = F.cosine_similarity(x, x_hat, dim=1).unsqueeze(1)
        euc_dist = torch.norm(x - x_hat, dim=1).unsqueeze(1)
        
        # Concatenate latent + errors
        z_c = torch.cat([z, cos_dist, euc_dist], dim=1)
        
        # Estimate mixture probabilities
        gamma = self.est(z_c)
        
        return z_c, x_hat, gamma
        
    def compute_gmm_params(self, z_c, gamma):
        N = z_c.size(0)
        sum_gamma = torch.sum(gamma, dim=0)
        
        phi = sum_gamma / N
        mu = torch.sum(gamma.unsqueeze(-1) * z_c.unsqueeze(1), dim=0) / sum_gamma.unsqueeze(-1)
        
        z_centered = z_c.unsqueeze(1) - mu.unsqueeze(0)
        
        cov = torch.sum(
            gamma.unsqueeze(-1).unsqueeze(-1) * torch.matmul(z_centered.unsqueeze(-1), z_centered.unsqueeze(-2)), 
            dim=0
        ) / sum_gamma.unsqueeze(-1).unsqueeze(-1)
        
        # Add diagonal epsilon for numerical stability
        eps = torch.eye(cov.size(1)).unsqueeze(0).to(cov.device) * 1e-6
        cov = cov + eps
        return phi, mu, cov
        
    def compute_energy(self, z_c, phi=None, mu=None, cov=None):
        if phi is None: phi = self.phi
        if mu is None: mu = self.mu
        if cov is None: cov = self.cov
        sample_energy = self._compute_energy(z_c, phi, mu, cov)
        return sample_energy
        
    def _compute_energy(self, z_c, phi, mu, cov):
        D = z_c.size(1)
        z_centered = z_c.unsqueeze(1) - mu.unsqueeze(0) # (N, n_gmm, D)
        
        try:
            cov_inv = torch.inverse(cov) # (n_gmm, D, D)
            det_cov = torch.det(cov) + 1e-12
        except RuntimeError:
            eps = torch.eye(cov.size(1)).unsqueeze(0).to(cov.device) * 1e-4
            cov_inv = torch.inverse(cov + eps)
            det_cov = torch.det(cov + eps) + 1e-12
        
        exp_term_tmp = -0.5 * torch.sum(torch.sum(z_centered.unsqueeze(-1) * cov_inv.unsqueeze(0), dim=-2) * z_centered, dim=-1)
        max_val = torch.max(exp_term_tmp, dim=1, keepdim=True)[0]
        exp_term = torch.exp(exp_term_tmp - max_val)
        
        sample_energy = -max_val.squeeze() - torch.log(torch.sum(phi.unsqueeze(0) * exp_term / (torch.sqrt((2 * np.pi)**D * det_cov)).unsqueeze(0), dim=1) + 1e-12)
        return sample_energy

# ----------------- System Globals ----------------- #
d_model = None
iso_forest = None
dagmm_threshold = 0.0

def train_synthetic_baseline():
    """
    Trains models on a synthetic healthy baseline to prepare for real-time anomaly detection.
    Features: [HeartRate, SpO2, Temp, Glucose, RespRate]
    """
    global d_model, iso_forest, dagmm_threshold
    print("Initializing Robust ML Anomaly Engine (DAGMM & Isolation Forest)...")
    
    # Generate 2000 "Healthy" physiological records
    N = 2000
    hr = np.random.normal(75, 5, N)        # 60-100 typical
    spo2 = np.random.normal(98, 1, N)      # 95-100
    temp = np.random.normal(36.6, 0.2, N)  # 36.1-37.2
    gluc = np.random.normal(100, 10, N)    # 70-140
    resp = np.random.normal(16, 2, N)      # 12-20
    
    # Clip to medical reality
    np.clip(spo2, a_min=None, a_max=100.0, out=spo2)
    
    X = np.column_stack((hr, spo2, temp, gluc, resp))
    X_tensor = torch.FloatTensor(X)

    # 1. Train Isolation Forest
    iso_forest = IsolationForest(contamination=0.01, random_state=42)
    iso_forest.fit(X)

    # 2. Train DAGMM Fast Mode
    d_model = DAGMM(in_dim=5)
    optimizer = torch.optim.Adam(d_model.parameters(), lr=1e-3)
    
    d_model.train()
    for epoch in range(50):
        optimizer.zero_grad()
        z_c, x_hat, gamma = d_model(X_tensor)
        
        # Reconstruction loss
        loss_recon = F.mse_loss(x_hat, X_tensor)
        
        # Calculate params sequentially across energy loss
        phi, mu, cov = d_model.compute_gmm_params(z_c, gamma)
        loss_energy = torch.mean(d_model.compute_energy(z_c, phi, mu, cov))
        
        loss = loss_recon + 0.1 * loss_energy
        loss.backward()
        optimizer.step()
        
    d_model.eval()
    with torch.no_grad():
        z_c, _, gamma = d_model(X_tensor)
        phi, mu, cov = d_model.compute_gmm_params(z_c, gamma)
        d_model.phi = phi
        d_model.mu = mu
        d_model.cov = cov
        energies = d_model.compute_energy(z_c, phi, mu, cov)
        # Threshold at 99th percentile of healthy data
        dagmm_threshold = np.percentile(energies.numpy(), 99)
        
    print("✅ ML Anomaly Engine Initialized Safely.")


def evaluate_vital_risk(hr, spo2, temp, gluc, resp):
    """
    Evaluates risk and determines if critical heart anomalies exist.
    """
    if d_model is None or iso_forest is None:
        train_synthetic_baseline()

    # Medical Baseline Bounds Assessment for Heart Risk
    med_risk = False
    reasons = []
    
    if hr > 120 or hr < 50:
        med_risk = True
        reasons.append(f"Heart Rate ({hr} bpm) is out of critical safe bounds.")
    if spo2 < 92:
        med_risk = True
        reasons.append(f"SpO2 ({spo2}%) reflects severe hypoxia.")
    if resp > 24 or resp < 10:
        med_risk = True
        reasons.append(f"Respiratory Rate ({resp} breaths/min) is indicating potential cardiopulmonary distress.")
        
    # Machine Learning Inference Assessment
    vec = np.array([[hr, spo2, temp, gluc, resp]])
    vec_t = torch.FloatTensor(vec)
    
    # Isolation Forest
    iso_pred = iso_forest.predict(vec)[0] # -1 for anomaly
    
    # DAGMM
    with torch.no_grad():
        z_c, _, _ = d_model(vec_t)
        energy = d_model.compute_energy(z_c).item()
        
    ml_risk = False
    if iso_pred == -1 or energy > dagmm_threshold:
        ml_risk = True
        reasons.append("Advanced ML (DAGMM/IF) correlation detected hidden high-risk physiological anomaly.")

    is_anomaly = med_risk or ml_risk
    
    rec = ""
    if is_anomaly:
        rec = "Seek immediate medical consultation. Rest and monitor vitals closely. Your doctor has been automatically alerted."
        
    return is_anomaly, "; ".join(reasons), rec
