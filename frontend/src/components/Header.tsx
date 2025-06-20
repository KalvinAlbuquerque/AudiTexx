// frontend/src/components/Header.tsx

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Importa o hook de autenticação

function Header() {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    
    // Hook para obter dados e funções de autenticação
    const { isAuthenticated, isAdmin, user, logout } = useAuth(); 

    const handleDropdownToggle = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    // Função para realizar o logout
    const handleLogout = () => {
        logout(); // Limpa o estado de autenticação
        navigate('/login'); // Redireciona para a página de login
    };

    return (
        <header
            className="text-white p-4 shadow-md relative"
            style={{
                backgroundImage: "url('/assets/fundo.png')",
                backgroundSize: 'cover',
                backgroundPosition: 'center',
            }}
        >
            <div className="container mx-auto flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <img 
                        src="/logo.png" 
                        alt="Logo Auditex" 
                        className="h-10 w-auto cursor-pointer" 
                        onClick={() => navigate('/')} 
                    />
                    <h1 
                        className="text-2xl font-bold cursor-pointer" 
                        onClick={() => navigate('/')}
                    >
                        Auditex
                    </h1>
                </div>
                <nav>
                    {/* Se o usuário ESTIVER autenticado, mostra a navegação completa */}
                    {isAuthenticated ? (
                        <ul className="flex items-center space-x-4 text-lg">
                            {/* Links de navegação padrão para todos os usuários logados */}
                            <li>
                                <button onClick={() => navigate('/lista-de-scans')} className="hover:text-blue-200 transition duration-300 ease-in-out">
                                    Listas
                                </button>
                            </li>
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
                            
                            {/* Menu Dropdown de Configurações */}
                            <li className="relative">
                                <button onClick={handleDropdownToggle} className="hover:text-blue-200 transition duration-300 ease-in-out focus:outline-none">
                                    Configurações
                                </button>
                                {isDropdownOpen && (
                                    <ul className="absolute right-0 mt-2 w-56 bg-white text-gray-800 rounded-md shadow-lg z-10">
                                        <li>
                                            <Link to="/manage-tenable-api-keys" className="block px-4 py-2 hover:bg-gray-200" onClick={() => setIsDropdownOpen(false)}>
                                                Gerenciar Chaves Tenable
                                            </Link>
                                        </li>
                                        <li>
                                            <Link to="/gerenciar-vulnerabilidades" className="block px-4 py-2 hover:bg-gray-200" onClick={() => setIsDropdownOpen(false)}>
                                                Gerenciar Vulnerabilidades
                                            </Link>
                                        </li>
                                    </ul>
                                )}
                            </li>

                            {/* Link que aparece SOMENTE para administradores */}
                            {isAdmin && (
                                <li>
                                    <button onClick={() => navigate('/manage-users')} className="hover:text-blue-200 transition duration-300 ease-in-out font-semibold">
                                        Gerenciar Usuários
                                    </button>
                                </li>
                            )}

                            {/* Informações do usuário e botão de Logout */}
                            <li className="pl-4">
                                <span className="text-gray-300">Olá, {user?.username}</span>
                            </li>
                            <li>
                                <button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition duration-300">
                                    Logout
                                </button>
                            </li>
                        </ul>
                    ) : (
                        /* Se o usuário NÃO ESTIVER autenticado, mostra apenas o botão de Login */
                        <ul className="flex items-center space-x-6 text-lg">
                            <li>
                                <button onClick={() => navigate('/login')} className="bg-[#007BB4] hover:bg-[#005f87] text-white font-bold py-2 px-4 rounded transition duration-300">
                                    Login
                                </button>
                            </li>
                        </ul>
                    )}
                </nav>
            </div>
        </header>
    );
}

export default Header;