import  { useState, useEffect } from 'react';
import { Link,  } from 'react-router-dom'; // Adicionado Link
// import axios from 'axios'; // Não precisamos mais de axios diretamente
// Removidos Header e Footer pois o layout é de sidebar
// import Header from '../components/Header';
// import Footer from '../components/Footer';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import ConfirmDeleteModal from '../pages/ConfirmDeleteModal';

// Importa as funções de API e interfaces
import { reportsApi, ReportGenerated } from '../api/backendApi';

function RelatoriosGerados() {
    const [relatorios, setRelatorios] = useState<ReportGenerated[]>([]);
    const [loading, setLoading] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [reportToDeleteId, setReportToDeleteId] = useState<string | null>(null);
    const [reportToDeleteName, setReportToDeleteName] = useState<string>('');
    const [dias, setDias] = useState(""); // Adicionado estado para os dias (filtro)


    useEffect(() => {
        fetchRelatorios();
    }, []);

    const fetchRelatorios = async () => {
        setLoading(true);
        try {
            const data = await reportsApi.getGeneratedReports();
            setRelatorios(data);
        } catch (error) {
            console.error('Erro ao buscar relatórios gerados:', error);
            toast.error('Erro ao buscar relatórios gerados.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async (idRelatorio: string) => {
        setLoading(true);
        try {
            const pdfBlob = await reportsApi.downloadReportPdf(idRelatorio);

            const url = window.URL.createObjectURL(pdfBlob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Relatorio_${idRelatorio}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success('Download do PDF iniciado!');
        } catch (error) {
            console.error('Erro ao baixar o PDF:', error);
            toast.error('Erro ao baixar o PDF. Verifique os logs.');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = (idRelatorio: string, nomeRelatorio: string) => {
        setReportToDeleteId(idRelatorio);
        setReportToDeleteName(nomeRelatorio);
        setShowDeleteModal(true);
    };

    const handleConfirmDelete = async () => {
        if (!reportToDeleteId) return;

        setLoading(true);
        try {
            const response = await reportsApi.deleteReport(reportToDeleteId);
            toast.success(response.message || 'Relatório excluído com sucesso!');
            fetchRelatorios(); // Recarrega os relatórios
        } catch (error: any) {
            console.error('Erro ao excluir relatório:', error);
            toast.error(error.response?.data?.error || 'Erro ao excluir relatório. Tente novamente.');
        } finally {
            setLoading(false);
            setShowDeleteModal(false);
            setReportToDeleteId(null);
            setReportToDeleteName('');
        }
    };

    const handleCancelDelete = () => {
        setShowDeleteModal(false);
        setReportToDeleteId(null);
        setReportToDeleteName('');
    };

    const handleDeleteAllReports = async () => {
        // O modal de confirmação para "Excluir Tudo" já é gerado pelo componente ConfirmDeleteModal
        // Não é mais necessário um window.confirm aqui diretamente.
        setReportToDeleteId(null); // Indica que é uma exclusão de todos
        setReportToDeleteName('TODOS os relatórios'); // Mensagem para o modal
        setShowDeleteModal(true); // Abre o modal
    };

    // Ação real de exclusão de todos os relatórios, chamada pelo ConfirmDeleteModal
    const confirmDeleteAll = async () => {
        setLoading(true);
        try {
            const response = await reportsApi.deleteAllReports();
            toast.success(response.message || 'Todos os relatórios foram excluídos com sucesso!');
            setRelatorios([]); // Limpa a lista no frontend
        } catch (error: any) {
            console.error('Erro ao excluir todos os relatórios:', error);
            toast.error(error.response?.data?.error || 'Erro ao excluir todos os relatórios. Tente novamente.');
        } finally {
            setLoading(false);
            setShowDeleteModal(false); // Fecha o modal após a ação
            setReportToDeleteId(null);
            setReportToDeleteName('');
        }
    }


    return (
        // Container principal: tela cheia, fundo com imagem, e display flex para dividir em colunas.
        <div
            className="min-h-screen bg-cover bg-center flex" // 'flex' aqui para criar as duas colunas
            style={{ backgroundImage: "url('/assets/fundo.png')" }} // Fundo azul com imagem
        >
            {/* Sidebar AZUL à esquerda (1/5 da largura da tela) */}
            <div className="w-1/5 #15688f text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen">
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg" // Caminho da nova logo da COGEL
                        alt="COGEL Logo"
                        className="w-32 h-auto mb-4"
                    />
                </Link>
                {/* Adicione outros links ou conteúdo para a sidebar aqui, se necessário */}
            </div>

            {/* Conteúdo central (área BRANCA à direita, 4/5 da largura da tela) */}
            <div className="w-4/5 bg-white flex flex-col p-8 min-h-screen"> {/* Flex-col para empilhar título, filtros e lista */}
                <h2 className="text-2xl font-bold text-gray-800 mb-6">
                    Relatórios Gerados
                </h2>

                {/* Barra de Filtro/Ação */}
                <div className="flex items-center space-x-4 mb-6">
                    <span className="text-black">Últimos</span>
                    <input
                        type="number"
                        value={dias}
                        onChange={(e) => setDias(e.target.value)}
                        className="border border-gray-300 rounded px-2 py-1 w-20 text-black focus:outline-none"
                        placeholder="0"
                        disabled={loading}
                    />
                    <span className="text-black">dias</span>
                    <button
                        onClick={fetchRelatorios} // Apenas para recarregar a lista, sem filtro de dias no backend atual
                        className="bg-[#007BB4] hover:bg-blue-600 text-white px-4 py-2 rounded transition cursor-pointer"
                        disabled={loading}
                    >
                        {loading ? <ClipLoader size={16} color={"#fff"} /> : 'Atualizar'}
                    </button>
                    <button
                        onClick={handleDeleteAllReports} // Abre o modal para exclusão total
                        className="bg-[#b95057] hover:bg-red-700 text-white px-4 py-2 rounded transition cursor-pointer ml-auto"
                        disabled={loading || relatorios.length === 0}
                    >
                        Excluir Tudo
                    </button>
                </div>

                {/* Área da Lista de Relatórios */}
                <div className="flex-1 bg-gray-100  rounded-md p-4 overflow-y-auto">
                    {loading && relatorios.length === 0 ? (
                        <div className="flex justify-center items-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : relatorios.length === 0 ? (
                        <div className="text-gray-500 text-center flex items-center justify-center h-full">
                            Nenhum relatório encontrado.
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-4">
                            {relatorios.map((relatorio) => (
                                <div
                                    key={relatorio.id}
                                    className="bg-white p-4 rounded-lg shadow-md flex justify-between items-center transition-all duration-300"
                                >
                                    <button
                                        onClick={() => handleDownloadPDF(relatorio.id)}
                                        className="text-blue-600 hover:underline cursor-pointer text-lg font-semibold bg-transparent border-none p-0 m-0"
                                    >
                                        {relatorio.nome}
                                    </button>
                                    <button
                                        onClick={() => handleDeleteClick(relatorio.id, relatorio.nome)}
                                        className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded text-sm transition duration-300"
                                    >
                                        Excluir
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
            {/* Modal de Confirmação de Exclusão */}
            {showDeleteModal && (
                <ConfirmDeleteModal
                    isOpen={showDeleteModal}
                    onClose={handleCancelDelete}
                    // Determina qual função de confirmação chamar baseado no que está sendo excluído
                    onConfirm={reportToDeleteId ? handleConfirmDelete : confirmDeleteAll}
                    message={reportToDeleteId
                        ? `Tem certeza que deseja excluir o relatório "${reportToDeleteName}"? Esta ação é irreversível.`
                        : `Tem certeza que deseja excluir TODOS os relatórios? Esta ação é irreversível e apagará todos os dados e arquivos.`}
                />
            )}
            <ToastContainer />
        </div>
    );
}

export default RelatoriosGerados;