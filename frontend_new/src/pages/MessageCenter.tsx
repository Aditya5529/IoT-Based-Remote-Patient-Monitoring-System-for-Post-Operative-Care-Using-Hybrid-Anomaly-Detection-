import React, { useEffect, useState, useRef } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Message {
    id: string;
    sender_id: string;
    content: string;
    timestamp: string;
    read: boolean;
}

interface UserSummary {
    id: string;
    full_name: string;
    role: string;
}

export default function MessageCenter() {
    const { user } = useAuth();
    const [users, setUsers] = useState<UserSummary[]>([]);
    const [selectedUser, setSelectedUser] = useState<UserSummary | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const bottomRef = useRef<HTMLDivElement>(null);

    // Fetch Contacts
    useEffect(() => {
        const fetchContacts = async () => {
            try {
                let res;
                if (user?.role === 'patient') {
                    res = await apiService.getMyDoctors();
                } else if (user?.role === 'doctor') {
                    res = await apiService.getMyPatients();
                } else {
                    res = await apiService.getPatients(); // Admin fallback
                }
                setUsers(res.data);

                if (res.data.length > 0 && !selectedUser) {
                    setSelectedUser(res.data[0]);
                }
            } catch (err) {
                console.error("Failed to fetch contacts", err);
            }
        };
        if (user) fetchContacts();
    }, [user]);

    // Poll Messages
    const fetchHistory = async (otherId: string) => {
        try {
            const res = await apiService.getMessages(otherId);
            setMessages(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        if (selectedUser) {
            fetchHistory(selectedUser.id);
            const interval = setInterval(() => fetchHistory(selectedUser.id), 3000); // 3s polling
            return () => clearInterval(interval);
        }
    }, [selectedUser]);

    // Scroll to bottom
    useEffect(() => {
        if (messages.length > 0) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedUser || !newMessage.trim()) return;

        try {
            await apiService.sendMessage({
                recipient_id: selectedUser.id,
                content: newMessage
            });
            setNewMessage('');
            fetchHistory(selectedUser.id);
        } catch (err) {
            console.error("Failed to send", err);
        }
    };

    return (
        <div className="flex h-[calc(100vh-2rem)] bg-white rounded-xl shadow overflow-hidden border">
            <div className="w-1/3 border-r bg-gray-50 p-4">
                <h2 className="font-bold text-lg mb-4">Contacts</h2>
                <div className="space-y-2 overflow-y-auto h-[calc(100vh-8rem)]">
                    {users.map(u => (
                        <div
                            key={u.id}
                            onClick={() => setSelectedUser(u)}
                            className={`p-3 rounded-lg cursor-pointer flex items-center transition-colors ${selectedUser?.id === u.id ? 'bg-blue-100 text-blue-800' : 'hover:bg-gray-100'}`}
                        >
                            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center mr-3 text-sm font-bold text-gray-600">
                                {u.full_name.charAt(0)}
                            </div>
                            <div>
                                <p className="font-medium text-sm">{u.full_name}</p>
                                <p className="text-xs text-gray-500 capitalize">{u.role}</p>
                            </div>
                        </div>
                    ))}
                    {users.length === 0 && <p className="text-gray-500 text-sm">No contacts found.</p>}
                </div>
            </div>

            <div className="flex-1 flex flex-col">
                {selectedUser ? (
                    <>
                        <div className="p-4 border-b bg-white font-semibold flex items-center shadow-sm z-10">
                            Chat with {selectedUser.full_name}
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-100">
                            {messages.length === 0 && <p className="text-center text-gray-400 mt-10">No messages yet. Say hi!</p>}
                            {messages.map(m => (
                                <div key={m.id} className={`flex ${m.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[70%] p-3 rounded-2xl shadow-sm text-sm ${m.sender_id === user?.id ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none'}`}>
                                        <p>{m.content}</p>
                                        <span className={`text-[10px] block mt-1 text-right ${m.sender_id === user?.id ? 'text-blue-200' : 'text-gray-400'}`}>
                                            {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            <div ref={bottomRef} />
                        </div>
                        <form onSubmit={handleSend} className="p-4 bg-white border-t flex gap-2">
                            <input
                                className="flex-1 border border-gray-300 p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                value={newMessage}
                                onChange={e => setNewMessage(e.target.value)}
                                placeholder="Type a message..."
                            />
                            <button disabled={!newMessage.trim()} className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">Send</button>
                        </form>
                    </>
                ) : (
                    <div className="flex-1 flex items-center justify-center text-gray-400 bg-gray-50">
                        <div className="text-center">
                            <p className="text-xl font-semibold text-gray-500">Welcome to Message Center</p>
                            <p className="mt-2 text-sm">Select a contact from the left to start chatting.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
