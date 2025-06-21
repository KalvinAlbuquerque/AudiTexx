import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ChangePasswordModal from '../pages/ChangePasswordModal'; 

function Header() {
    const navigate = useNavigate();
    const { isAuthenticated, isAdmin, user, logout } = useAuth();

    const [isConfigOpen, setConfigOpen] = useState(false);
    const [isUserMenuOpen, setUserMenuOpen] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <>
            <header className="text-white p-4">
                <div className="container mx-auto flex items-center justify-between">
                    {/* Agrupamento do Título e Navegação Principal (Lado Esquerdo) */}
                    <div className="flex items-center space-x-6">
                        {/* Título (Logo foi movida) */}
                        <h1 
                            className="text-2xl font-bold cursor-pointer" 
                            onClick={() => navigate('/')}
                        >
                            Auditex
                        </h1>

                        {/* Navegação Principal */}
                        {isAuthenticated && (
                            <nav>
                                <ul className="flex items-center space-x-4 text-lg">
                                    <li>
                                        <button onClick={() => navigate('/scans')} className="hover:text-blue-200 transition duration-300 ease-in-out">
                                            Scans
                                        </button>
                                    </li>
                                    <li>
                                        <button onClick={() => navigate('/relatorios')} className="hover:text-blue-200 transition duration-300 ease-in-out">
                                            Relatórios
                                        </button>
                                    </li>
                                    
                                    <li className="relative">
                                        <button onClick={() => setConfigOpen(!isConfigOpen)} className="hover:text-blue-200 transition duration-300 ease-in-out focus:outline-none">
                                            Configurações
                                        </button>
                                        {isConfigOpen && (
                                            <ul className="absolute left-0 mt-2 w-56 bg-white text-gray-800 rounded-md shadow-lg z-10">
                                                <li>
                                                    <Link to="/manage-tenable-api-keys" className="block px-4 py-2 hover:bg-gray-200" onClick={() => setConfigOpen(false)}>
                                                        Gerenciar Chaves Tenable
                                                    </Link>
                                                </li>
                                                <li>
                                                    <Link to="/gerenciar-vulnerabilidades" className="block px-4 py-2 hover:bg-gray-200" onClick={() => setConfigOpen(false)}>
                                                        Gerenciar Vulnerabilidades
                                                    </Link>
                                                </li>
                                                {isAdmin && (
                                                <>
                                                    <li>
                                                        <Link 
                                                            to="/manage-users" 
                                                            className="block px-4 py-2 hover:bg-gray-200" 
                                                            onClick={() => setConfigOpen(false)}
                                                        >
                                                            Gerenciar Usuários
                                                        </Link>
                                                    </li>
                                                    <li>
                                                        <Link 
                                                            to="/logs" 
                                                            className="block px-4 py-2 hover:bg-gray-200" 
                                                            onClick={() => setConfigOpen(false)}
                                                        >
                                                            Logs
                                                        </Link>
                                                    </li>
                                                </>
                                            )}
                                            </ul>
                                        )}
                                    </li>
                                </ul>
                            </nav>
                        )}
                    </div>

                    {/* Menu do Usuário, Botão de Login e Logo (Lado Direito) */}
                    <div className="flex items-center space-x-4">
                        {isAuthenticated ? (
                            <div className="relative">
                                <button onClick={() => setUserMenuOpen(!isUserMenuOpen)} className="flex items-center space-x-2 hover:text-blue-200 transition duration-300 ease-in-out focus:outline-none">
                                    <span>{user?.username.toUpperCase()}</span>
                                    <svg className={`w-4 h-4 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                </button>
                                {isUserMenuOpen && (
                                    <ul className="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded-md shadow-lg z-10">
                                        <li>
                                            <button 
                                                onClick={() => {
                                                    setIsModalOpen(true);
                                                    setUserMenuOpen(false);
                                                }} 
                                                className="w-full text-left block px-4 py-2 hover:bg-gray-200"
                                            >
                                                Alterar Senha
                                            </button>
                                        </li>
                                        <li>
                                            <button onClick={handleLogout} className="w-full text-left block px-4 py-2 hover:bg-gray-200">
                                                Logout
                                            </button>
                                        </li>
                                    </ul>
                                )}
                            </div>
                        ) : (
                            <button onClick={() => navigate('/login')} className="bg-[#007BB4] hover:bg-[#005f87] text-white font-bold py-2 px-4 rounded transition duration-300">
                                Login
                            </button>
                        )}

                        {/* Logo movida para o extremo direito */}
                        <img 
                            src="/logo.png" 
                            alt="Logo Auditex" 
                            className="h-10 w-auto cursor-pointer" 
                            onClick={() => navigate('/')} 
                        />
                    </div>
                </div>
            </header>

            <ChangePasswordModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </>
    );
}

export default Header;