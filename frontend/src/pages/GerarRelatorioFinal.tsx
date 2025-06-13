import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // Importar useNavigate
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify'; // Importar toast e ToastContainer
import 'react-toastify/dist/ReactToastify.css';

import { reportsApi } from '../api/backendApi';
import MissingVulnerabilitiesModal from './MissingVulnerabilitiesModal'; // Importar o modal

function GerarRelatorioFinal() {
    const { relatorioId } = useParams<{ relatorioId: string }>();
    const navigate = useNavigate(); // Hook para navegação

    const [loading, setLoading] = useState(false);
    const [missingVulnerabilities, setMissingVulnerabilities] = useState<{ sites: string[]; servers: string[] } | null>(null);
    const [isSitesModalOpen, setIsSitesModalOpen] = useState(false); // Estado para abrir modal de sites
    const [isServersModalOpen, setIsServersModalOpen] = useState(false); // Estado para abrir modal de servers

    useEffect(() => {
        if (relatorioId) {
            fetchMissingVulnerabilities();
        }
    }, [relatorioId]);

    const fetchMissingVulnerabilities = async () => {
        setLoading(true);
        try {
            const missingSites = await reportsApi.getMissingVulnerabilities(relatorioId!, 'sites');
            const missingServers = await reportsApi.getMissingVulnerabilities(relatorioId!, 'servers');
            
            setMissingVulnerabilities({ sites: missingSites, servers: missingServers });

            if (missingSites.length > 0 || missingServers.length > 0) {
                toast.warn('Foram encontradas vulnerabilidades não descritas. Verifique a seção de vulnerabilidades ausentes.');
            } else {
                toast.success('Relatório gerado e todas as vulnerabilidades foram categorizadas.');
            }
        } catch (error) {
            console.error('Erro ao buscar vulnerabilidades ausentes:', error);
            toast.error('Erro ao buscar vulnerabilidades ausentes.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPdf = async () => {
        if (!relatorioId) {
            toast.error('ID do relatório não disponível para download.');
            return;
        }
        setLoading(true);
        try {
            const pdfBlob = await reportsApi.downloadReportPdf(relatorioId);
            const url = window.URL.createObjectURL(pdfBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Relatorio_Auditoria_${relatorioId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            toast.success('Download do relatório PDF iniciado!');
        } catch (error) {
            console.error('Erro ao baixar PDF:', error);
            toast.error('Erro ao baixar o relatório PDF.');
        } finally {
            setLoading(false);
        }
    };

    const handleBackToHome = () => {
      navigate('/'); // Navega para a página inicial
    };

    return (
        <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">Status do Relatório</h1>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <ClipLoader size={50} color={"#1a73e8"} />
                </div>
            ) : (
                <div className="bg-white shadow-md rounded-lg p-6 mb-8 w-full max-w-2xl">
                    <p className="text-lg text-gray-700 text-center mb-4">
                        Processo de geração do relatório concluído para o ID: <span className="font-semibold">{relatorioId}</span>
                    </p>

                    {/* Botão de Download do PDF */}
                    <div className="text-center mb-6">
                        <button
                            onClick={handleDownloadPdf}
                            className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-2 px-4 rounded transition"
                            disabled={loading}
                        >
                            Baixar Relatório PDF
                        </button>
                    </div>

                    {missingVulnerabilities && (
                        <>
                            {missingVulnerabilities.sites.length > 0 && (
                                <div className="mb-4 flex justify-between items-center bg-red-100 p-3 rounded">
                                    <h2 className="text-xl font-semibold text-red-600">Vulnerabilidades WebApp Ausentes:</h2>
                                    <button
                                        onClick={() => setIsSitesModalOpen(true)}
                                        className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-1 px-3 rounded text-sm transition" // Corrigido
                                    >
                                        Visualizar ({missingVulnerabilities.sites.length})
                                    </button>
                                </div>
                            )}

                            {missingVulnerabilities.servers.length > 0 && (
                                <div className="mb-4 flex justify-between items-center bg-red-100 p-3 rounded">
                                    <h2 className="text-xl font-semibold text-red-600">Vulnerabilidades Servidor Ausentes:</h2>
                                    <button
                                        onClick={() => setIsServersModalOpen(true)}
                                        className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-1 px-3 rounded text-sm transition" // Corrigido
                                    >
                                        Visualizar ({missingVulnerabilities.servers.length})
                                    </button>
                                </div>
                            )}

                            {missingVulnerabilities.sites.length === 0 && missingVulnerabilities.servers.length === 0 && (
                                <p className="text-green-600 text-center text-lg mt-4">
                                    Todas as vulnerabilidades foram categorizadas e descritas!
                                </p>
                            )}
                        </>
                    )}

                    {/* Botão para voltar à página inicial */}
                    <div className="text-center mt-6">
                        <button
                            onClick={handleBackToHome}
                            className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-2 px-4 rounded transition" // Corrigido
                        >
                            Voltar para o Início
                        </button>
                    </div>
                </div>
            )}

            {/* Modal para Vulnerabilidades WebApp Ausentes */}
            {missingVulnerabilities && (
                <MissingVulnerabilitiesModal
                    isOpen={isSitesModalOpen}
                    onClose={() => setIsSitesModalOpen(false)}
                    title="Vulnerabilidades WebApp Ausentes"
                    vulnerabilities={missingVulnerabilities.sites}
                />
            )}

            {/* Modal para Vulnerabilidades Servidor Ausentes */}
            {missingVulnerabilities && (
                <MissingVulnerabilitiesModal
                    isOpen={isServersModalOpen}
                    onClose={() => setIsServersModalOpen(false)}
                    title="Vulnerabilidades Servidor Ausentes"
                    vulnerabilities={missingVulnerabilities.servers}
                />
            )}

            <ToastContainer />
        </div>
    );
}

export default GerarRelatorioFinal;