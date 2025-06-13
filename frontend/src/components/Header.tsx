import { useNavigate } from 'react-router-dom';

function Header() {
    const navigate = useNavigate();

    return (
        <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4 shadow-md">
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
                    </ul>
                </nav>
            </div>
        </header>
    );
}

export default Header;