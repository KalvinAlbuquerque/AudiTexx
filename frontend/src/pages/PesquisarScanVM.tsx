import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Select from 'react-select';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Importa as funções de API e interfaces
import { scansApi, listsApi, ScanData } from '../api/backendApi';

// Interface para o tipo de opção do react-select
interface SelectOption {
    value: string;
    label: string;
}

function PesquisarScanVM() {
    const [scanName, setScanName] = useState('');
    const [foundScan, setFoundScan] = useState<ScanData | null>(null);
    const [loading, setLoading] = useState(false);
    const [listaSelecionada, setListaSelecionada] = useState(''); // Para associar a uma lista existente
    const [listasDisponiveis, setListasDisponiveis] = useState<SelectOption[]>([]); // Opções para o Select de listas

    const navigate = useNavigate();

    React.useEffect(() => {
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

    const handleSearchScan = async () => {
        if (!scanName.trim()) {
            toast.warn('Por favor, digite o nome do scan VM.');
            return;
        }
        setLoading(true);
        try {
            const scan = await scansApi.getVMScanByName(scanName.trim());
            setFoundScan(scan);
            if (!scan) {
                toast.info('Nenhum scan VM encontrado com este nome.');
            }
        } catch (error) {
            console.error('Erro ao buscar scan VM:', error);
            toast.error('Erro ao buscar scan VM.');
            setFoundScan(null);
        } finally {
            setLoading(false);
        }
    };

    const handleListaChange = (selectedOption: SelectOption | null) => {
        setListaSelecionada(selectedOption ? selectedOption.value : '');
    };

    const handleDownloadScan = async () => {
        if (!foundScan) {
            toast.warn('Nenhum scan selecionado para download.');
            return;
        }
        if (!listaSelecionada) {
            toast.warn('Selecione uma lista para associar o scan VM.');
            return;
        }

        setLoading(true);
        try {
            const listas = await listsApi.getAllLists();
            const listaEncontrada = listas.find(lista => lista.nomeLista === listaSelecionada);

            if (!listaEncontrada) {
                toast.error('Lista selecionada não encontrada.');
                setLoading(false);
                return;
            }

            // --- INÍCIO DA CORREÇÃO APLICADA AQUI PARA REPLICAR COMPORTAMENTO ANTERIOR ---
            // No código antigo, 'id' do resultado recebia data.uuid, e 'id_scan' recebia data.id.
            // Para VM scans, a API retorna um objeto com 'id' (numérico) e 'uuid'.
            // Vamos assumir que 'foundScan.uuid' contém o UUID e 'foundScan.id' contém o ID numérico.
            // Se foundScan.uuid for 'undefined', o scan talvez não tenha um UUID principal
            // ou a propriedade esteja em outro lugar.
            
            // O debug anterior mostrou: vmScanDownloadId: 399, vmScanHistoryUuid: undefined
            // Isso indica que foundScan.id está correto (399).
            // E foundScan.history?.last_modification_date ou foundScan.history[x].uuid não está funcionando.

            // Com base no seu código antigo, você estava enviando:
            // idScan: resultado?.id  (que era data.uuid)
            // idNmr: resultado?.id_scan (que era data.id)

            // Então, agora precisamos extrair:
            // 1. O UUID do scan (para `idScan` no `listsApi.addVMScanToList`)
            // 2. O ID numérico do scan (para `idNmr` no `listsApi.addVMScanToList` E para `idScan` no `scansApi.downloadVMScan`)

            // Vamos assumir que a API para `getScanByName` retorna `foundScan.uuid` para o UUID e `foundScan.id` para o numérico.
            // A interface ScanData já tem `id?: string;` mas não tem `uuid?: string;` diretamente.
            // A API Tenable para `/scans` (VM) geralmente retorna ambos `id` (numérico) e `uuid`.
            // Para ser compatível com o `ScanData` atual, vamos tentar acessar `foundScan.uuid` diretamente.
            // Se `foundScan.uuid` não existir (pois não está na interface ou no retorno da API),
            // isso pode ser o problema.

            const vmScanNumericId: string | undefined = foundScan.id; // Este é o 'data.id' do seu código antigo
            let vmScanUuid: string | undefined;

            // Tentativa de obter o UUID do scan VM:
            // 1. Se a API Tenable retorna 'uuid' diretamente no objeto foundScan (o que é comum para VM)
            vmScanUuid = (foundScan as any).uuid; // Acessa como 'any' para contornar o tipo se não estiver na interface ScanData

            // 2. Fallback para o histórico (se vmScanUuid ainda for undefined e houver histórico)
            // Isso cobre o caso em que 'uuid' não está no root, mas no histórico (menos comum para o principal UUID do scan VM)
            if (!vmScanUuid && foundScan.history && foundScan.history.length > 0) {
                // Pega o UUID do histórico mais recente
                const latestHistory = foundScan.history.reduce((prev: any, current: any) => {
                    const prevDate = new Date(prev.last_modification_date || 0).getTime();
                    const currentDate = new Date(current.last_modification_date || 0).getTime();
                    return (prevDate > currentDate) ? prev : current;
                }, foundScan.history[0]);
                vmScanUuid = latestHistory.uuid;
            }
            
            // Log para depuração
            console.log("DEBUG - vmScanNumericId (ID numérico do scan):", vmScanNumericId);
            console.log("DEBUG - vmScanUuid (UUID do scan ou histórico):", vmScanUuid);


            // Verificação final dos IDs antes de usar
            if (!vmScanNumericId || !vmScanUuid) {
                toast.error('Dados de ID do scan ou History ID incompletos. Verifique se o scan possui um UUID principal e um histórico.');
                setLoading(false);
                return;
            }
            // --- FIM DA CORREÇÃO APLICADA AQUI PARA REPLICAR COMPORTAMENTO ANTERIOR ---


            // Chama a API do backend para baixar o CSV
            // O backend 'downloadVMScan' espera (nomeListaId, idScan, historyId)
            // Onde 'idScan' é o ID numérico e 'historyId' é o UUID do histórico.
            // Para replicar o comportamento, usaremos vmScanNumericId como 'idScan' e vmScanUuid como 'historyId'.
            await scansApi.downloadVMScan(
                listaEncontrada.idLista,
                vmScanNumericId, // Passa o ID numérico do scan
                vmScanUuid // Passa o UUID (que funcionava como historyId no seu código antigo)
            );

            // Adiciona ou atualiza as informações do scan VM na lista no banco de dados
            // O backend 'addVMScanToList' espera (nomeLista, idScan, nomeScan, criadoPor, idNmr)
            // Onde 'idScan' é o UUID e 'idNmr' é o ID numérico.
            await listsApi.addVMScanToList(
                listaEncontrada.nomeLista,
                vmScanUuid, // UUID para 'idScan'
                foundScan.name,
                foundScan.owner?.name || 'N/A',
                vmScanNumericId // ID numérico para 'idNmr'
            );

            toast.success('Scan VM baixado e associado à lista com sucesso!');
            setFoundScan(null);
            setScanName('');
            navigate(`/editar-lista/${listaEncontrada.idLista}`);
        } catch (error) {
            console.error('Erro ao baixar ou associar scan VM:', error);
            toast.error('Erro ao baixar ou associar scan VM.');
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
                className="w-1/5 #15688f text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen"
            >
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg"
                        alt="COGEL Logo"
                        className="w-32 h-auto"
                    />
                </Link>
            </div>

            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md min-h-screen flex flex-col">
                <h1 className="text-2xl font-bold mb-6 text-gray-800">
                    Pesquisar Scans - Vulnerability Management
                </h1>

                <div className="flex flex-col space-y-2 max-w-md mx-auto mt-10 w-full">
                    <label className="block font-semibold text-black">Nome do Scan</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded text-black"
                        placeholder="Digite o nome do scan"
                        value={scanName}
                        onChange={(e) => setScanName(e.target.value)}
                    />
                    <div className="flex justify-center">
                        <button
                            onClick={handleSearchScan}
                            className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-blue-600 cursor-pointer"
                            disabled={loading}
                        >
                            {loading ? <ClipLoader size={20} color={"#fff"} /> : "Pesquisar"}
                        </button>
                    </div>
                </div>

                {foundScan && (
                    <div className="mt-6 bg-gray-100 rounded-lg overflow-y-auto p-4 flex-1" style={{minHeight: '200px'}}>
                        <div className="space-y-2 text-gray-800">
                            <p><strong>Nome do Scan:</strong> {foundScan.name}</p>
                            <p><strong>ID (Numérico):</strong> {foundScan.id || 'N/A'}</p>
                            {/* Adicionado log para UUID principal do scan se existir */}
                            {(foundScan as any).uuid && (
                                <p><strong>UUID (Principal do Scan):</strong> {(foundScan as any).uuid}</p>
                            )}
                            {/* Adicionado log para histórico de VM */}
                            {foundScan.history && foundScan.history.length > 0 && (
                                <p><strong>Último Histórico VM (UUID):</strong> {foundScan.history[foundScan.history.length - 1].uuid || 'N/A'}</p>
                            )}
                            <p><strong>Proprietário:</strong> {foundScan.owner?.name || 'N/A'}</p>

                            <div className="mt-4">
                                <label htmlFor="listaSelecionada" className="block text-gray-700 text-sm font-bold mb-2">
                                    Associar a uma Lista Existente:
                                </label>
                                <Select<SelectOption>
                                    id="listaSelecionada"
                                    options={listasDisponiveis}
                                    onChange={handleListaChange}
                                    value={listasDisponiveis.find(option => option.value === listaSelecionada)}
                                    placeholder="Selecione uma lista"
                                    isClearable
                                    isDisabled={loading}
                                />
                            </div>

                            <div className="text-center mt-6">
                                <button
                                    onClick={handleDownloadScan}
                                    className="bg-[#007BB4] hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                                    disabled={loading || !listaSelecionada}
                                >
                                    {loading ? <ClipLoader size={20} color={"#fff"} /> : 'Baixar e Associar Scan'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
                {!loading && !foundScan && (
                    <div className="mt-4 h-[400px] bg-gray-100 rounded-lg overflow-y-auto p-4 flex-1">
                        <div className="flex items-center justify-center h-full">
                            <p className="text-center text-gray-500">Nenhum scan encontrado.</p>
                        </div>
                    </div>
                )}
            </div>
            <ToastContainer />
        </div>
    );
}

export default PesquisarScanVM;