import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { usersApi, User } from '../api/backendApi';
import ConfirmDeleteModal from './ConfirmDeleteModal';

function ManageUsers() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    
    // Estados para o modal de criação
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [newUser, setNewUser] = useState({ username: '', password: '', role: 'user', email: ''});

    // Estados para o modal de exclusão
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [userToDelete, setUserToDelete] = useState<User | null>(null);

    // Estados para o modal de edição
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [userToEdit, setUserToEdit] = useState<User | null>(null);
    const [newPassword, setNewPassword] = useState('');


    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const fetchedUsers = await usersApi.getAllUsers();
            setUsers(fetchedUsers);
        } catch (error) {
            console.error('Erro ao buscar usuários:', error);
            toast.error('Não foi possível carregar os usuários.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newUser.username.trim() || !newUser.password.trim() || !newUser.email.trim()) {
            toast.warn('Nome de usuário, e-mail e senha são obrigatórios.');
            return;
        }
        setLoading(true);
        try {
            await usersApi.createUser(newUser);
            toast.success('Usuário criado com sucesso!');
            setIsCreateModalOpen(false);
            setNewUser({ username: '', password: '', role: 'user', email: '' });
            fetchUsers();
        } catch (error: any) {
            toast.error(error.response?.data?.error || 'Erro ao criar usuário.');
        } finally {
            setLoading(false);
        }
    };

    const handleEditClick = (user: User) => {
        setUserToEdit(user);
        setNewPassword(''); // Limpa o campo de senha anterior
        setIsEditModalOpen(true);
    };

    const handleUpdatePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userToEdit || !newPassword.trim()) {
            toast.warn('A nova senha não pode estar em branco.');
            return;
        }
        setLoading(true);
        try {
            await usersApi.updateUserPassword(userToEdit.public_id, newPassword);
            toast.success(`Senha do usuário "${userToEdit.username}" atualizada com sucesso!`);
            setIsEditModalOpen(false);
            setUserToEdit(null);
        } catch (error: any) {
             toast.error(error.response?.data?.error || 'Erro ao atualizar a senha.');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = (user: User) => {
        setUserToDelete(user);
        setIsDeleteModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (!userToDelete) return;
        setLoading(true);
        try {
            await usersApi.deleteUser(userToDelete.public_id);
            toast.success(`Usuário "${userToDelete.username}" excluído com sucesso!`);
            setUserToDelete(null);
            setIsDeleteModalOpen(false);
            fetchUsers();
        } catch (error: any) {
            toast.error(error.response?.data?.error || 'Erro ao excluir usuário.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-grow bg-cover bg-center flex" style={{ backgroundImage: "url('/assets/fundo.png')" }}>
            <div className="w-1/5 text-white flex flex-col items-center justify-center p-4 shadow-lg">
                <Link to="/"><img src="/assets/logocogel.jpg" alt="COGEL Logo" className="w-32 h-auto" /></Link>
            </div>
            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md flex flex-col">
                 <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-800">Gerenciar Usuários</h1>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="bg-[#007BB4] text-white px-4 py-2 rounded hover:bg-[#005f87] transition cursor-pointer"
                    >
                        + Adicionar Usuário
                    </button>
                </div>
                <div className="flex-1 bg-gray-100 rounded-md p-4 overflow-y-auto">
                    {loading && users.length === 0 ? (
                        <div className="flex justify-center items-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : (
                         <table className="w-full text-left table-auto">
                            <thead className="bg-gray-200">
                                <tr>
                                    <th className="px-4 py-2">Username</th>
                                    <th className="px-4 py-2">Email</th>
                                    <th className="px-4 py-2">Role</th>
                                    <th className="px-4 py-2 text-right">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.public_id} className="border-b hover:bg-gray-50">
                                        <td className="px-4 py-2 text-black">{user.username}</td>
                                        <td className="px-4 py-2 text-black">{user.email}</td>
                                        <td className="px-4 py-2 text-black">{user.role}</td>
                                        <td className="px-4 py-2 text-right space-x-2">
                                            <button
                                                onClick={() => handleEditClick(user)}
                                                className="bg-[#007BB4] hover:bg-[#005f87] text-white px-3 py-1 rounded  transition"
                                                disabled={loading}
                                            >
                                                Editar
                                            </button>
                                            <button
                                                onClick={() => handleDeleteClick(user)}
                                                className="bg-[#007BB4] hover:bg-[#005f87] text-white px-3 py-1 rounded  transition"
                                                disabled={loading}
                                            >
                                                Excluir
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Modal de Criação de Usuário */}
            {isCreateModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">Novo Usuário</h2>
                        <form onSubmit={handleCreateUser}>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">Username</label>
                                <input type="text" id="username" value={newUser.username} onChange={(e) => setNewUser({ ...newUser, username: e.target.value })} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" required />
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">Email</label>
                                <input type="email" id="email" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" required />
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">Password</label>
                                <input type="password" id="password" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700" required />
                            </div>
                            <div className="mb-6">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="role">Role</label>
                                <select id="role" value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700">
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div className="flex justify-end space-x-4">
                                <button type="button" onClick={() => setIsCreateModalOpen(false)} className="bg-gray-300 hover:bg-gray-400 text-black px-4 py-2 rounded">Cancelar</button>
                                <button type="submit" className="bg-[#007BB4] hover:bg-[#005f87] text-white px-4 py-2 rounded" disabled={loading}>
                                    {loading ? <ClipLoader size={20} color="#fff" /> : 'Criar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            
            {/* Modal de Edição de Senha */}
            {isEditModalOpen && userToEdit && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">
                            Alterar Senha para <span className="text-[#007BB4]">{userToEdit.username}</span>
                        </h2>
                        <form onSubmit={handleUpdatePassword}>
                            <div className="mb-6">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new-password">
                                    Nova Senha
                                </label>
                                <input
                                    type="password"
                                    id="new-password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"
                                    placeholder="Digite a nova senha"
                                    required
                                />
                            </div>
                            <div className="flex justify-end space-x-4">
                                <button
                                    type="button"
                                    onClick={() => setIsEditModalOpen(false)}
                                    className="bg-gray-300 hover:bg-gray-400 text-black px-4 py-2 rounded"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="bg-[#007BB4] hover:bg-[#005f87] text-white px-4 py-2 rounded"
                                    disabled={loading}
                                >
                                    {loading ? <ClipLoader size={20} color="#fff" /> : 'Salvar Alterações'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Confirmação de Exclusão */}
            {isDeleteModalOpen && userToDelete && (
                 <ConfirmDeleteModal
                    isOpen={isDeleteModalOpen}
                    onClose={() => setIsDeleteModalOpen(false)}
                    onConfirm={handleConfirmDelete}
                    message={`Tem certeza que deseja excluir o usuário "${userToDelete.username}"? Esta ação não pode ser desfeita.`}
                />
            )}

            <ToastContainer />
        </div>
    );
}

export default ManageUsers;