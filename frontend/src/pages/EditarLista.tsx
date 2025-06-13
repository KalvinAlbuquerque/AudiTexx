import  { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
// Removido o import de listsApi
// import { listsApi, scansApi, Lista, ScanData } from '../api/backendApi'; 
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Importa axios temporariamente para chamadas diretas
import axios from 'axios'; 

// Importa apenas o necessário do backendApi.ts para tipagem
import { ScanData, Lista } from '../api/backendApi'; 

function EditarLista() {
    const { idLista } = useParams<{ idLista: string }>();
    const navigate = useNavigate();

    const [nomeLista, setNomeLista] = useState('');
    const [scansWebApp, setScansWebApp] = useState<ScanData[]>([]);
    const [vmScanName, setVmScanName] = useState('');
    const [vmScanCriadoPor, setVmScanCriadoPor] = useState('');
    const [loading, setLoading] = useState(false);

    // Hardcode a URL base da API para este teste temporário
    const API_BASE_URL = 'http://localhost:5000';

    useEffect(() => {
        if (idLista) {
            fetchListaDetalhes();
        }
    }, [idLista]);

    const fetchListaDetalhes = async () => {
        setLoading(true);
        try {
            // CORREÇÃO TEMPORÁRIA: Chamada direta para lists/getTodasAsListas
            const response = await axios.get(`${API_BASE_URL}/lists/getTodasAsListas/`); 
            const listas: Lista[] = response.data; // Assumimos que o backend retorna uma lista de Listas
            const lista = listas.find((l: Lista) => l.idLista === idLista); // Acessa diretamente

            if (lista) {
                setNomeLista(lista.nomeLista);
                await fetchScansAssociados(lista.nomeLista); // Busca scans WAS
                await fetchVMScansAssociados(lista.nomeLista); // Busca info VM
            } else {
                toast.error('Lista não encontrada.');
                navigate('/lista-de-scans');
            }
        } catch (error) {
            console.error('Erro ao buscar detalhes da lista:', error);
            toast.error('Erro ao buscar detalhes da lista.');
        } finally {
            setLoading(false);
        }
    };

    const fetchScansAssociados = async (nomeListaAtual: string) => {
        try {
            // Chamada direta para listas/getScansDeLista
            const response = await axios.post(`${API_BASE_URL}/lists/getScansDeLista/`, { nomeLista: nomeListaAtual });
            const associatedScanNames: string[] = response.data;
            setScansWebApp(associatedScanNames.map((name: string) => ({ name: name } as ScanData)));
        } catch (error) {
            console.error('Erro ao buscar scans associados:', error);
            toast.error('Erro ao buscar scans associados.');
            setScansWebApp([]);
        }
    };

    const fetchVMScansAssociados = async (nomeListaAtual: string) => {
        try {
            // Chamada direta para lists/getVMScansDeLista
            const response = await axios.post(`${API_BASE_URL}/lists/getVMScansDeLista/`, { nomeLista: nomeListaAtual });
            const vmScanData: [string, string] = response.data; // Assumimos que retorna [nome, criador]
            if (vmScanData && vmScanData.length === 2) {
                setVmScanName(vmScanData[0]);
                setVmScanCriadoPor(vmScanData[1]);
            } else {
                setVmScanName('');
                setVmScanCriadoPor('');
            }
        } catch (error: any) {
            console.error('Erro ao buscar VM scan associado:', error);
            toast.error('Erro ao buscar VM scan associado.');
        }
    };

    const handleAtualizar = async () => {
        if (!nomeLista.trim()) {
            toast.warn('O nome da lista não pode estar vazio.');
            return;
        }
        setLoading(true);
        try {
            if (idLista) {
                // Chamada direta para lists/editarNomeLista
                await axios.post(`${API_BASE_URL}/lists/editarNomeLista/`, { id: idLista, novoNome: nomeLista.trim() });
                toast.success('Nome da lista atualizado com sucesso!');
            } else {
                toast.error('ID da lista não disponível para atualização.');
            }
        } catch (error: any) {
            console.error('Erro ao atualizar nome da lista:', error);
            if (axios.isAxiosError(error) && error.response && error.response.status === 409) {
                toast.error('Já existe uma lista com esse nome.');
            } else {
                toast.error('Erro ao atualizar nome da lista.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleRemover = async () => {
        setLoading(true);
        try {
            // Chamada direta para lists/limparScansDeLista
            await axios.post(`${API_BASE_URL}/lists/limparScansDeLista/`, { nomeLista: nomeLista });
            toast.success('Scans de WebApp da lista limpos com sucesso!');
            setScansWebApp([]);
        } catch (error) {
            console.error('Erro ao limpar scans de WebApp:', error);
            toast.error('Erro ao limpar scans de WebApp.');
        } finally {
            setLoading(false);
        }
    };

    const handleRemoverVM = async () => {
        setLoading(true);
        try {
            // Chamada direta para lists/limparVMScansDeLista
            await axios.post(`${API_BASE_URL}/lists/limparVMScansDeLista/`, { nomeLista: nomeLista });
            toast.success('Informações de VM Scan da lista limpas com sucesso!');
            setVmScanName('');
            setVmScanCriadoPor('');
        } catch (error) {
            console.error('Erro ao limpar VM Scan:', error);
            toast.error('Erro ao limpar VM Scan.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="min-h-screen bg-cover bg-center flex"
            style={{ backgroundImage: "url('/assets/fundo.png')" }}
        >
            <div
                className="w-1/5 text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen"
            >
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg"
                        alt="COGEL Logo"
                        className="w-32 h-auto"
                    />
                </Link>
            </div>

            <div className="w-4/5 p-8 bg-[#F9FCFD] rounded-l-lg shadow-md flex flex-col min-h-screen">
                <h1 className="text-2xl font-bold mb-6 text-black">Editar Lista: {nomeLista}</h1>

                <div className="flex items-end mb-6 space-x-4">
                    <div>
                        <label className="block text-black font-medium mb-1">Nome da Lista</label>
                        <input
                            type="text"
                            value={nomeLista}
                            onChange={(e) => setNomeLista(e.target.value)}
                            className="border border-gray-300 rounded px-4 py-2 w-72 focus:outline-none text-black"
                            disabled={loading}
                        />
                    </div>

                    <button
                        onClick={handleAtualizar}
                        className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-[#005f87] transition cursor-pointer"
                        disabled={loading}
                    >
                        {loading ? <ClipLoader size={16} color={"#fff"} /> : 'Atualizar'}
                    </button>
                </div>

                <div className="flex justify-end mb-4">
                    <button
                        onClick={handleRemover}
                        className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-[#005f87] transition cursor-pointer"
                        disabled={loading || scansWebApp.length === 0}
                    >
                        {loading ? <ClipLoader size={16} color={"#fff"} /> : 'Limpar Lista de WAS'}
                    </button>
                </div>

                <div className="bg-gray-100 rounded-md flex-1 p-4 overflow-y-auto">
                    {loading && scansWebApp.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : scansWebApp.length === 0 ? (
                        <div className="text-gray-500 text-center flex items-center justify-center h-full">
                            Sem scans de WebApp na lista.
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-4">
                            {scansWebApp.map((scan, index) => (
                                <div key={scan.name || index} className="bg-white p-4 rounded-lg shadow-md transition-all duration-300">
                                    <p className="text-black">{scan.name}</p>
                                    <p className="text-sm text-gray-600">{scan.target}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="flex justify-end mt-4">
                    <button
                        onClick={handleRemoverVM}
                        className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-[#005f87] transition cursor-pointer"
                        disabled={loading || (!vmScanName && !vmScanCriadoPor)}
                    >
                        {loading ? <ClipLoader size={16} color={"#fff"} /> : 'Limpar Lista de VM'}
                    </button>
                </div>

                <div className="bg-gray-100 rounded-md p-4 mt-6">
                    {loading && (!vmScanName && !vmScanCriadoPor) ? (
                         <div className="flex items-center justify-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : (vmScanName || vmScanCriadoPor) ? (
                        <div className="bg-white p-4 rounded-lg shadow-md transition-all duration-300">
                            <p className="text-black font-semibold">Nome do Scan:</p>
                            <p className="text-black">{vmScanName}</p>
                            <p className="text-black font-semibold mt-2">Criado Por:</p>
                            <p className="text-black">{vmScanCriadoPor}</p>
                        </div>
                    ) : (
                        <div className="text-gray-500 flex items-center justify-center h-full">
                            Sem informações de VM Scan disponíveis.
                        </div>
                    )}
                </div>
            </div>
            <ToastContainer />
        </div>
    );
}

export default EditarLista;