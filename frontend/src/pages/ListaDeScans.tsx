import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import ConfirmDeleteModal from '../pages/ConfirmDeleteModal'; 
import { listsApi } from '../api/backendApi';
interface Lista {
    idLista: string;
    nomeLista: string;
    relatorioGerado?: boolean;
}

function ListaDeScans() {
    const [listas, setListas] = useState<Lista[]>([]);
    const [loading, setLoading] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [listToDeleteId, setListToDeleteId] = useState<string | null>(null);
    const [listToDeleteName, setListToDeleteName] = useState<string>('');
    const [listaSelecionada, setListaSelecionada] = useState<Lista | null>(null);

    const navigate = useNavigate();

    useEffect(() => {
        fetchListas();
    }, []);

    const fetchListas = async () => {
        setLoading(true);
        try {
            // Usando a função centralizada do serviço de API
            const data = await listsApi.getAllLists();
            setListas(data);
        } catch (error: any) {
            console.error("Erro ao buscar listas:", error);
            const errorMessage = error.response?.data?.error || "Erro ao buscar listas.";
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    const handleSelecionar = (lista: Lista) => {
        setListaSelecionada(lista);
    };

    const handleEditList = () => {
        if (listaSelecionada) {
            navigate(`/editar-lista/${listaSelecionada.idLista}`); 
        } else {
            toast.warn('Selecione uma lista para editar.');
        }
    };

    const handleDeleteClick = () => {
        if (!listaSelecionada) {
            toast.warn('Selecione uma lista para remover.');
            return;
        }
        setListToDeleteId(listaSelecionada.idLista);
        setListToDeleteName(listaSelecionada.nomeLista);
        setShowDeleteModal(true);
    };

    const handleConfirmDelete = async () => {
        if (!listToDeleteId) return;

        setLoading(true);
        try {
            // Usando a função centralizada do serviço de API
            const responseData = await listsApi.deleteList(listToDeleteId);
            toast.success(responseData.message || 'Lista excluída com sucesso!');
            
            setListaSelecionada(null);
            fetchListas(); // Recarrega a lista após a exclusão
        } catch (error: any) {
            console.error('Erro ao remover lista:', error);
            const errorMessage = error.response?.data?.error || 'Ocorreu um erro ao remover a lista.';
            toast.error(errorMessage);
        } finally {
            setLoading(false);
            setShowDeleteModal(false);
            setListToDeleteId(null);
            setListToDeleteName('');
        }
    };


    const handleCancelDelete = () => {
        setShowDeleteModal(false);
        setListToDeleteId(null);
        setListToDeleteName('');
    };

    // NOVO: Função para lidar com o clique no botão "Gerar Relatório"
    const handleGenerateReport = () => {
        if (listaSelecionada) {
            navigate(`/gerar-relatorio/${listaSelecionada.idLista}`);
        } else {
            toast.warn('Selecione uma lista para gerar o relatório.');
        }
    };


    return (
        <div
            className="flex-grow bg-cover bg-center flex"
            style={{ backgroundImage: "url('/assets/fundo.png')" }}
        >
            {/* Sidebar AZUL à esquerda com a cor #15688f */}
            <div
                className="w-1/5 text-white flex flex-col items-center justify-center p-4 shadow-lg "
            >
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg"
                        alt="COGEL Logo"
                        className="w-32 h-auto"
                    />
                </Link>
            </div>

            {/* Conteúdo central (área BRANCA à direita, 4/5 da largura da tela) */}
            <div className="w-4/5 p-8 bg-[#F9FCFD] rounded-l-lg shadow-md flex flex-col">
                {/* Título */}
                <h1 className="text-2xl font-bold text-black mb-4">Listas de Scans</h1>

                {/* Botões alinhados à direita */}
                <div className="flex justify-end space-x-4 mb-4">
                    <button
                        onClick={() => navigate("/criar-lista")}
                        className="bg-[#007BB4] text-white px-4 py-2 rounded hover:bg-[#005f87] transition cursor-pointer"
                        disabled={loading}
                    >
                        {loading ? <ClipLoader size={16} color={"#fff"} /> : '+ Adicionar Lista'}
                    </button>

                    <button
                        disabled={!listaSelecionada || loading}
                        onClick={handleEditList}
                        className={`px-4 py-2 rounded transition ${
                            listaSelecionada
                                ? "bg-[#007BB4] text-white hover:bg-[#005f87] cursor-pointer"
                                : "bg-gray-400 text-white cursor-not-allowed"
                        }`}
                    >
                        Editar Lista
                    </button>

                    <button
                        disabled={!listaSelecionada || loading}
                        onClick={handleDeleteClick}
                        className={`px-4 py-2 rounded transition ${
                            listaSelecionada
                                ? "bg-[#007BB4] text-white hover:bg-[#005f87] cursor-pointer"
                                : "bg-gray-400 text-white cursor-not-allowed"
                        }`}
                    >
                        Remover Lista
                    </button>

                    {/* NOVO BOTÃO: Gerar Relatório */}
                    <button
                        disabled={!listaSelecionada || loading}
                        onClick={handleGenerateReport}
                        className={`px-4 py-2 rounded transition ${
                            listaSelecionada
                              ? "bg-[#007BB4] text-white hover:bg-[#005f87] cursor-pointer"
                                : "bg-gray-400 text-white cursor-not-allowed"
                        }`}
                    >
                        Gerar Relatório
                    </button>
                </div>

                {/* Área da lista */}
                {loading && listas.length === 0 ? (
                    <div className="flex-1 flex items-center justify-center h-full">
                        <ClipLoader size={50} color={"#1a73e8"} />
                    </div>
                ) : listas.length === 0 ? (
                    <div className="flex-1 flex items-center justify-center h-full">
                        <p className="text-gray-500 text-center">Nenhuma lista disponível.</p>
                    </div>
                ) : (
                    <div className="bg-gray-100 flex-1 rounded-md p-4 overflow-y-auto">
                        <ul className="space-y-2">
                            {listas.map((lista) => (
                                <li
                                    key={lista.idLista}
                                    className={`p-3 rounded cursor-pointer border border-gray-200 ${
                                        listaSelecionada?.idLista === lista.idLista
                                            ? "bg-[#007BB4] text-white"
                                            : "bg-white hover:bg-gray-200 text-black"
                                    }`}
                                    onClick={() => handleSelecionar(lista)}
                                >
                                    {lista.nomeLista}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
            {showDeleteModal && (
                <ConfirmDeleteModal
                    isOpen={showDeleteModal}
                    onClose={handleCancelDelete}
                    onConfirm={handleConfirmDelete}
                    message={`Tem certeza que deseja excluir a lista "${listToDeleteName}"? Esta ação é irreversível e apagará todos os dados e arquivos relacionados.`}
                />
            )}
            <ToastContainer />
        </div>
    );
}

export default ListaDeScans;