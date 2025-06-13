import { useState } from 'react'; // Importar useState
import { useNavigate, Link } from 'react-router-dom';

function Header() {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // Estado para controlar o menu suspenso

    const handleDropdownToggle = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    return (
        <header
            className="text-white p-4 shadow-md relative" // Adicionado 'relative' para o posicionamento do dropdown
            style={{
                backgroundImage: "url('/assets/fundo.png')", // Adicionado fundo.png
                backgroundSize: 'cover',
                backgroundPosition: 'center',
            }}
        >
            <div className="container mx-auto flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    {/* Logotipo/Nome da Aplicação */}
                    <img src="/logo.png" alt="Logo Auditex" className="h-10 w-auto cursor-pointer" onClick={() => navigate('/')} />
                    <h1 className="text-2xl font-bold cursor-pointer" onClick={() => navigate('/')}>
                        Auditex
                    </h1>
                </div>
                <nav>
                    <ul className="flex space-x-6 text-lg">
                        <li>
                            <button
                                onClick={() => navigate('/lista-de-scans')}
                                className="hover:text-blue-200 transition duration-300 ease-in-out"
                            >
                                Listas de Scans
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => navigate('/scans')}
                                className="hover:text-blue-200 transition duration-300 ease-in-out"
                            >
                                Scans
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => navigate('/relatorios')}
                                className="hover:text-blue-200 transition duration-300 ease-in-out"
                            >
                                Relatórios
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => navigate('/gerenciar-vulnerabilidades')}
                                className="hover:text-blue-200 transition duration-300 ease-in-out"
                            >
                                Gerenciar Vulnerabilidades
                            </button>
                        </li>
                        {/* Novo item de menu suspenso */}
                        <li className="relative">
                            <button
                                onClick={handleDropdownToggle}
                                className="hover:text-blue-200 transition duration-300 ease-in-out focus:outline-none"
                            >
                                Configurações
                            </button>
                            {isDropdownOpen && (
                                <ul className="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded-md shadow-lg z-10">
                                    <li>
                                        <Link
                                            to="/manage-tenable-api-keys" // Rota para a nova página
                                            className="block px-4 py-2 hover:bg-gray-200"
                                            onClick={() => setIsDropdownOpen(false)} // Fecha o dropdown ao clicar
                                        >
                                            Tenable API
                                        </Link>
                                    </li>
                                    {/* Adicione outras opções aqui, se necessário */}
                                </ul>
                            )}
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    );
}

export default Header;