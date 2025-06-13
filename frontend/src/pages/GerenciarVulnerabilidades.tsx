import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { vulnerabilitiesApi } from '../api/backendApi';

interface VulnerabilityData {
    Vulnerabilidade: string;
    Categoria: string;
    Subcategoria: string;
    Descrição: string;
    Solução: string;
    Imagem?: string;
}

interface DescritivoData {
    categoria: string;
    descricao: string;
    subcategorias?: { subcategoria: string; descricao: string }[];
}

function GerenciarVulnerabilidades() {
    const [selectedVulnType, setSelectedVulnType] = useState<'sites' | 'servers'>('sites'); 
    const [vulnerabilities, setVulnerabilities] = useState<VulnerabilityData[]>([]);
    const [descritivos, setDescritivos] = useState<DescritivoData[]>([]);
    const [vulnSelecionada, setVulnSelecionada] = useState<VulnerabilityData | null>(null); 
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState<VulnerabilityData>({ 
        Vulnerabilidade: '',
        Categoria: '',
        Subcategoria: '',
        Descrição: '',
        Solução: '',
        Imagem: '',
    });
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [formMode, setFormMode] = useState<"add" | "edit">("add");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [error, setError] = useState<string | null>(null);


    useEffect(() => {
        fetchVulnerabilities(selectedVulnType);
        fetchDescritivos(selectedVulnType);
    }, [selectedVulnType]);

    const handleSelectVuln = (vuln: VulnerabilityData) => {
        setVulnSelecionada(vuln);
    };

    const fetchVulnerabilities = async (type: 'sites' | 'servers') => {
        setLoading(true);
        setError(null);
        try {
            const data = await vulnerabilitiesApi.getAllVulnerabilities(type);
            setVulnerabilities(data);
        } catch (err: any) {
            console.error('Erro ao buscar vulnerabilidades:', err);
            setError(err.message || 'Erro ao carregar vulnerabilidades.');
            setVulnerabilities([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchDescritivos = async (type: 'sites' | 'servers') => {
        try {
            const data = await vulnerabilitiesApi.getDescriptiveVulnerabilities(type);
            setDescritivos(data);
        } catch (error) {
            console.error('Erro ao buscar descritivos:', error);
            toast.error('Erro ao buscar descritivos.');
            setDescritivos([]);
        }
    };

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        } else {
            setSelectedFile(null);
        }
    };

    const handleAddClick = () => {
        setFormMode("add");
        setFormData({
            Vulnerabilidade: '',
            Categoria: '',
            Subcategoria: '',
            Descrição: '',
            Solução: '',
            Imagem: '',
        });
        setSelectedFile(null);
        setIsModalOpen(true);
    };

    const handleEditClick = () => {
        if (vulnSelecionada) {
            setFormMode("edit");
            setFormData({ ...vulnSelecionada });
            setSelectedFile(null);
            setIsModalOpen(true);
        } else {
            toast.warn("Selecione uma vulnerabilidade para editar.");
        }
    };

    const handleFormSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        if (!formData.Vulnerabilidade || !formData.Categoria || !formData.Subcategoria || !formData.Descrição || !formData.Solução) {
            toast.warn('Preencha todos os campos obrigatórios.');
            setLoading(false);
            return;
        }

        const dataToSend = { ...formData };
        let imagePath = formData.Imagem || '';

        if (selectedFile) {
            const formDataForUpload = new FormData();
            formDataForUpload.append('image', selectedFile);
            formDataForUpload.append('categoria', formData.Categoria);
            formDataForUpload.append('subcategoria', formData.Subcategoria);
            formDataForUpload.append('vulnerabilidade', formData.Vulnerabilidade);

            try {
                const uploadResponse = await vulnerabilitiesApi.uploadImage(formDataForUpload);
                imagePath = uploadResponse.imagePath;
                toast.info('Imagem enviada com sucesso!');
            } catch (uploadError: any) {
                console.error('Erro ao enviar imagem:', uploadError);
                toast.error(uploadError.message || 'Erro ao enviar imagem. Verifique os logs.');
                setLoading(false);
                return;
            }
        }
        dataToSend.Imagem = imagePath;

        try {
            let response;
            if (formMode === "add") {
                response = await vulnerabilitiesApi.addVulnerability(selectedVulnType, dataToSend);
            } else {
                if (!vulnSelecionada || !vulnSelecionada.Vulnerabilidade) {
                    toast.error('Nenhuma vulnerabilidade selecionada para atualização.');
                    setLoading(false);
                    return;
                }
                response = await vulnerabilitiesApi.updateVulnerability(selectedVulnType, vulnSelecionada.Vulnerabilidade, dataToSend);
            }
            toast.success(response.message || (formMode === "add" ? 'Vulnerabilidade adicionada!' : 'Vulnerabilidade atualizada!'));
            
            setVulnSelecionada(null);
            setFormData({ Vulnerabilidade: '', Categoria: '', Subcategoria: '', Descrição: '', Solução: '', Imagem: '' });
            setSelectedFile(null);
            setIsModalOpen(false);
            fetchVulnerabilities(selectedVulnType);
        } catch (error: any) {
            console.error('Erro ao salvar vulnerabilidade:', error);
            toast.error(error.response?.data?.error || 'Erro ao salvar vulnerabilidade.');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = async () => {
        if (!vulnSelecionada || !vulnSelecionada.Vulnerabilidade) {
            toast.warn('Selecione uma vulnerabilidade para excluir.');
            return;
        }
        if (!window.confirm(`Tem certeza que deseja excluir a vulnerabilidade "${vulnSelecionada.Vulnerabilidade}"?`)) {
            return;
        }
        setLoading(true);
        try {
            const response = await vulnerabilitiesApi.deleteVulnerability(selectedVulnType, vulnSelecionada.Vulnerabilidade);
            toast.success(response.message || 'Vulnerabilidade excluída com sucesso!');
            setVulnSelecionada(null);
            fetchVulnerabilities(selectedVulnType);
        } catch (error: any) {
            console.error('Erro ao excluir vulnerabilidade:', error);
            toast.error(error.response?.data?.error || 'Erro ao excluir vulnerabilidade.');
        } finally {
            setLoading(false);
        }
    };

    const getUniqueCategories = () => {
        const categories = new Set<string>();
        descritivos.forEach(d => categories.add(d.categoria));
        return Array.from(categories);
    };


    const filteredVulnerabilities = vulnerabilities.filter((vuln) =>
        vuln.Vulnerabilidade.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vuln.Categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
        vuln.Subcategoria.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const subcategoriasFiltradas = descritivos.find(
        (cat) => cat.categoria === formData.Categoria
    )?.subcategorias || [];


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

            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md min-h-screen flex flex-col">
                <h1 className="text-xl font-bold text-gray-800 mb-4">Gerenciar Vulnerabilidades</h1>

                <div className="mb-4 flex space-x-4">
                    <button
                        className={`px-4 py-2 rounded-md font-medium ${
                            selectedVulnType === 'sites' ? 'bg-[#007BB4] text-white' : 'bg-gray-200 text-black hover:bg-gray-300'
                        }`}
                        onClick={() => setSelectedVulnType('sites')}
                    >
                        Gerenciar Vulnerabilidades de Sites
                    </button>
                    <button
                        className={`px-4 py-2 rounded-md font-medium ${
                            selectedVulnType === 'servers' ? 'bg-[#007BB4] text-white' : 'bg-gray-200 text-black hover:bg-gray-300'
                        }`}
                        onClick={() => setSelectedVulnType('servers')}
                    >
                        Gerenciar Vulnerabilidades de Servidores
                    </button>
                </div>

                <input
                    type="text"
                    placeholder="Pesquisar por categoria, subcategoria ou vulnerabilidade..."
                    className="w-full p-2 border border-gray-300 rounded-md mb-4 text-black"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    disabled={loading}
                />

                <div className="bg-gray-100 h-80 overflow-y-auto rounded-md p-4 mb-6">
                    {loading && filteredVulnerabilities.length === 0 ? (
                        <div className="flex justify-center items-center h-full">
                            <ClipLoader size={50} color={"#1a73e8"} />
                        </div>
                    ) : error ? (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-red-500">Erro: {error}</p>
                        </div>
                    ) : filteredVulnerabilities.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-gray-500">Nenhuma vulnerabilidade encontrada para {selectedVulnType === 'sites' ? 'sites' : 'servidores'}.</p>
                        </div>
                    ) : (
                        <ul className="space-y-2">
                            {filteredVulnerabilities.map((vuln) => (
                                <li
                                    key={vuln.Vulnerabilidade}
                                    className={`p-3 rounded cursor-pointer border border-gray-200 ${
                                        vulnSelecionada?.Vulnerabilidade === vuln.Vulnerabilidade
                                            ? "bg-[#007BB4] text-white"
                                            : "bg-white hover:bg-gray-200 text-black"
                                    }`}
                                    onClick={() => handleSelectVuln(vuln)}
                                >
                                    <p className="font-semibold">{vuln.Vulnerabilidade}</p>
                                    <p className="text-sm">
                                        Categoria: {vuln.Categoria} | Subcategoria: {vuln.Subcategoria}
                                    </p>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <div className="flex justify-end space-x-4 mt-auto">
                    <button
                        className="px-6 py-2 rounded text-white font-medium bg-green-600 hover:bg-green-700"
                        onClick={handleAddClick}
                        disabled={loading}
                    >
                        Adicionar
                    </button>
                    <button
                        className={`px-6 py-2 rounded text-white font-medium ${
                            vulnSelecionada ? "bg-yellow-600 hover:bg-yellow-700" : "bg-gray-400 cursor-not-allowed"
                        }`}
                        disabled={!vulnSelecionada || loading}
                        onClick={handleEditClick}
                    >
                        Editar
                    </button>
                    <button
                        className={`px-6 py-2 rounded text-white font-medium ${
                            vulnSelecionada ? "bg-red-600 hover:bg-red-700" : "bg-gray-400 cursor-not-allowed"
                        }`}
                        disabled={!vulnSelecionada || loading}
                        onClick={handleDeleteClick}
                    >
                        Excluir
                    </button>
                </div>
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-8 rounded-lg shadow-xl w-1/2 max-h-[90vh] overflow-y-auto">
                        <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">
                            {formMode === "add" ? "Adicionar Nova Vulnerabilidade" : "Editar Vulnerabilidade"}
                        </h2>
                        <form onSubmit={handleFormSubmit}>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="Vulnerabilidade">
                                    Nome da Vulnerabilidade:
                                </label>
                                <input
                                    type="text"
                                    id="Vulnerabilidade"
                                    name="Vulnerabilidade"
                                    value={formData.Vulnerabilidade}
                                    onChange={handleFormChange}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    required
                                    disabled={formMode === "edit" || loading}
                                />
                                {formMode === "edit" && <p className="text-xs text-gray-500 mt-1">O nome da vulnerabilidade não pode ser alterado diretamente.</p>}
                            </div>

                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="Categoria">
                                    Categoria:
                                </label>
                                <select
                                    id="Categoria"
                                    name="Categoria"
                                    value={formData.Categoria}
                                    onChange={handleFormChange}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    required
                                    disabled={loading}
                                >
                                    <option value="">Selecione uma Categoria</option>
                                    {getUniqueCategories().map(cat => (
                                        <option key={cat} value={cat}>{cat}</option>
                                    ))}
                                </select>
                            </div>

                               <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="Subcategoria">
                                    Subcategoria:
                                </label>
                                <select
                                    id="Subcategoria"
                                    name="Subcategoria"
                                    value={formData.Subcategoria}
                                    onChange={handleFormChange}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    required
                                    disabled={loading || !formData.Categoria}
                                >
                                    <option value="">Selecione uma Subcategoria</option>
                                    {subcategoriasFiltradas.map((subcat) => (
                                        <option key={subcat.subcategoria} value={subcat.subcategoria}>
                                            {subcat.subcategoria} 
                                        </option>
                                    ))}
                                </select>
                                {!formData.Categoria && <p className="text-xs text-gray-500 mt-1">Selecione uma categoria primeiro para ver as subcategorias.</p>}
                            </div>
                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="Descrição">
                                    Descrição:
                                </label>
                                <textarea
                                    id="Descrição"
                                    name="Descrição"
                                    value={formData.Descrição}
                                    onChange={handleFormChange}
                                    rows={4}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    required
                                    disabled={loading}
                                ></textarea>
                            </div>

                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="Solução">
                                    Solução:
                                </label>
                                <textarea
                                    id="Solução"
                                    name="Solução"
                                    value={formData.Solução}
                                    onChange={handleFormChange}
                                    rows={4}
                                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                    required
                                    disabled={loading}
                                ></textarea>
                            </div>

                            <div className="mb-4">
                                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="ImagemUpload">
                                    Upload da Imagem (PNG, JPG, JPEG, GIF):
                                </label>
                                <input
                                    type="file"
                                    id="ImagemUpload"
                                    name="ImagemUpload"
                                    accept=".png,.jpg,.jpeg,.gif"
                                    onChange={handleFileChange}
                                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                                    disabled={loading}
                                />
                                {formData.Imagem && !selectedFile && (
                                    <p className="text-sm text-gray-600 mt-2">
                                        Imagem atual: <span className="text-gray-700">{formData.Imagem}</span> 
                                    </p>
                                )}
                                {selectedFile && (
                                    <p className="text-sm text-gray-600 mt-2">
                                        Arquivo selecionado: {selectedFile.name}
                                    </p>
                                )}
                            </div>

                            <div className="flex justify-end space-x-4 mt-6">
                                <button
                                    type="button"
                                    className="px-6 py-2 rounded text-black font-medium bg-gray-300 hover:bg-gray-400"
                                    onClick={() => setIsModalOpen(false)}
                                    disabled={loading}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-6 py-2 rounded text-white font-medium bg-[#007BB4] hover:bg-[#009BE2]"
                                    disabled={loading}
                                >
                                    {loading ? <ClipLoader size={20} color={"#fff"} /> : (formMode === "add" ? "Adicionar" : "Salvar Alterações")}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
            <ToastContainer />
        </div>
    );
}

export default GerenciarVulnerabilidades;