import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; // Correção: Garante a importação correta do CSS do Toastify

import { scansApi, listsApi, ScanData } from '../api/backendApi';

interface SelectOption {
    value: string;
    label: string;
}

function PesquisarScanWAS() {
    const [nomeUsuario, setNomeUsuario] = useState('');
    const [nomePasta, setNomePasta] = useState('');
    const [scans, setScans] = useState<ScanData[]>([]);
    const [scansSelecionados, setScansSelecionados] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [nomeLista, setNomeLista] = useState('');
    const [listasDisponiveis, setListasDisponiveis] = useState<SelectOption[]>([]);
    const [selectAll, setSelectAll] = useState(false);

    useEffect(() => {
        const fetchListas = async () => {
            try {
                const listas = await listsApi.getAllLists();
                const options: SelectOption[] = listas.map(lista => ({ value: lista.nomeLista, label: lista.nomeLista }));
                setListasDisponiveis(options);
            } catch (error) {
                console.error('Erro ao buscar listas disponíveis:', error);
                toast.error('Erro ao buscar listas disponíveis.');
            }
        };
        fetchListas();
    }, []);

    const handlePesquisa = async () => {
        if (!nomeUsuario.trim() || !nomePasta.trim()) {
            toast.warn('Por favor, preencha os campos de Usuário e Pasta.');
            return;
        }
        setIsLoading(true);
        try {
            const fetchedScans = await scansApi.getWebAppScansFromFolder(nomeUsuario.trim(), nomePasta.trim());
            setScans(fetchedScans);
            setScansSelecionados([]);
            setSelectAll(false);
            if (fetchedScans.length === 0) {
                toast.info('Nenhum scan encontrado com os critérios fornecidos.');
            }
        } catch (error) {
            console.error('Erro ao buscar scans:', error);
            toast.error('Erro ao buscar scans. Verifique os logs.');
            setScans([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleToggleScan = (config_id: string | undefined) => {
        if (!config_id) return;
        setScansSelecionados(prev => {
            const newSelection = prev.includes(config_id)
                ? prev.filter(id => id !== config_id)
                : [...prev, config_id];
            setSelectAll(newSelection.length === scans.length && scans.length > 0);
            return newSelection;
        });
    };

    const handleSelectAll = () => {
        if (scans.length === 0) return;

        if (selectAll) {
            setScansSelecionados([]);
        } else {
            const allConfigIds = scans.map(scan => scan.config_id).filter((id): id is string => id !== undefined);
            setScansSelecionados(allConfigIds);
        }
        setSelectAll(!selectAll);
    };

    const openModal = () => {
        if (scansSelecionados.length === 0) {
            toast.warn('Selecione pelo menos um scan para adicionar à lista.');
            return;
        }
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setNomeLista('');
    };

    const handleAddToList = async () => {
        if (!nomeLista.trim()) {
            toast.warn("Por favor, digite o nome da lista.");
            return;
        }

        setIsLoading(true);
        try {
            const selectedScansData = {
                items: scans.filter(scan => scan.config_id && scansSelecionados.includes(scan.config_id))
            };

            await listsApi.addWebAppScanToList(nomeLista.trim(), selectedScansData);
            toast.success("Scans adicionados à lista com sucesso!");
            closeModal();
            setScansSelecionados([]);
            setSelectAll(false);
        } catch (error: any) {
            console.error("Erro ao adicionar à lista:", error);
            toast.error(error.response?.data?.error || "Erro desconhecido ao adicionar à lista.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div
            className="min-h-screen bg-cover bg-center flex"
            style={{
                backgroundImage: "url('/assets/fundo.png')",
                cursor: isLoading ? "wait" : "default",
            }}
        >
            {/* Sidebar */}
            <div className="w-1/5 #15688f text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen"
            >
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg"
                        alt="COGEL Logo"
                        className="w-32 h-auto"
                    />
                </Link>
            </div>

            {/* Main content area (right side) */}
            {/* Alterado para h-screen para fixar a altura na viewport */}
            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md h-screen flex flex-col">
                <h1 className="text-2xl font-bold mb-6 text-gray-800">Pesquisar Scans - Web App</h1>

                {/* Search inputs and button */}
                <div className="flex flex-col space-y-4 max-w-sm mb-6">
                    <div>
                        <label className="block font-semibold mb-1 text-black">Nome Usuário</label>
                        <input
                            type="text"
                            className="w-full p-2 border border-gray-300 rounded text-black"
                            id="nome-usuario"
                            value={nomeUsuario}
                            onChange={(e) => setNomeUsuario(e.target.value)}
                            disabled={isLoading}
                        />
                    </div>

                    <div>
                        <label className="block font-semibold mb-1 text-black">Nome Pasta</label>
                        <input
                            type="text"
                            className="w-full p-2 border border-gray-300 rounded text-black"
                            id="nome-pasta"
                            value={nomePasta}
                            onChange={(e) => setNomePasta(e.target.value)}
                            disabled={isLoading}
                        />
                    </div>

                    <button
                        onClick={handlePesquisa}
                        className="bg-[#007BB4] text-white px-4 py-2 rounded hover:bg-blue-600 w-fit cursor-pointer"
                        disabled={isLoading}
                    >
                        {isLoading ? <ClipLoader size={20} color={"#fff"} /> : "Pesquisar"}
                    </button>
                </div>

                {/* Select All, Add to List buttons and total scans */}
                {/* Usando mt-auto para empurrar este bloco para o final do espaço disponível, antes da lista */}
                <div className="flex justify-between items-end mt-auto space-x-2">
                    <button
                        onClick={handleSelectAll}
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 text-sm cursor-pointer"
                        disabled={scans.length === 0 || isLoading}
                    >
                        {selectAll ? "Desselecionar Todos" : "Selecionar Todos"}
                    </button>
                    <div className="flex flex-col items-end space-y-2">
                        <button
                            onClick={openModal}
                            className="bg-[#007BB4] text-white px-4 py-2 rounded hover:bg-blue-600 text-sm cursor-pointer"
                            disabled={scansSelecionados.length === 0 || isLoading}
                        >
                            + Adicionar Scans Selecionados à Lista ({scansSelecionados.length})
                        </button>
                        <span className="text-sm text-gray-700">
                            Total de scans encontrados: {scans.length}
                        </span>
                    </div>
                </div>

                {/* Área da lista de scans com rolagem.
                    flex-1: faz este elemento preencher o espaço restante verticalmente.
                    overflow-y-auto: Adiciona barra de rolagem Y apenas quando o conteúdo transborda.
                    mt-4: Espaçamento entre o bloco de botões e a lista.
                    p-2: Padding interno para a lista.
                */}
                <div className="flex-1 mt-4 bg-gray-100 rounded-lg overflow-y-auto p-2">
                    {isLoading && scans.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : scans.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-center text-gray-500">Nenhum scan encontrado.</p>
                        </div>
                    ) : (
                        <ul className="space-y-2">
                            {scans.map((scan) => (
                                <li key={scan.config_id || scan.name} className="p-3 bg-white rounded shadow-sm flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        checked={scan.config_id ? scansSelecionados.includes(scan.config_id) : false}
                                        onChange={() => handleToggleScan(scan.config_id)}
                                        className="form-checkbox h-5 w-5 text-blue-600 rounded"
                                        disabled={isLoading}
                                    />
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-800">{scan.name}</h3>
                                        <p className="text-gray-600">{scan.description}</p>
                                        <p className="text-sm text-gray-500">Target: {scan.target}</p>
                                        <p className="text-sm text-gray-500">Criado em: {new Date(scan.created_at || '').toLocaleString()}</p>
                                        <p className="text-sm text-gray-500">Último Status: {scan.last_scan?.status}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-md w-1/3 max-w-md">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Adicionar Scans à Lista</h2>
                        <label className="block font-semibold mb-1 text-black">Selecione a Lista</label>
                        <select
                            value={nomeLista}
                            onChange={(e) => setNomeLista(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mb-4"
                            disabled={isLoading}
                        >
                            <option value="">Selecione uma lista</option>
                            {listasDisponiveis.map(option => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                        </select>
                        <div className="flex justify-end space-x-4">
                            <button
                                onClick={closeModal}
                                className="bg-gray-300 text-black px-4 py-2 rounded hover:bg-gray-400 cursor-pointer"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleAddToList}
                                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 cursor-pointer"
                                disabled={isLoading || !nomeLista.trim()}
                            >
                                {isLoading ? "Adicionando..." : "Adicionar"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <ToastContainer />
        </div>
    );
}

export default PesquisarScanWAS;