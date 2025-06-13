import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Importa Link
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Importa as funções de API
import { listsApi } from '../api/backendApi';

function CriarLista() {
    const [nomeLista, setNomeLista] = useState('');
    const [loading, setLoading] = useState(false);
    // Removidos alertMessage e handleCloseAlert, pois estamos usando react-toastify
    // const [alertMessage, setAlertMessage] = useState<string | null>(null);
    // const handleCloseAlert = () => setAlertMessage(null);

    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!nomeLista.trim()) {
            toast.warn('O nome da lista não pode ser vazio.');
            return;
        }

        setLoading(true);
        try {
            const response = await listsApi.createList(nomeLista.trim());
            toast.success(response.message || 'Lista criada com sucesso!');
            setNomeLista(''); // Limpa o campo após o sucesso
            navigate('/lista-de-scans'); // Redireciona para a lista de scans
        } catch (error: any) {
            console.error('Erro ao criar lista:', error);
            if (error.response && error.response.status === 409) {
                toast.error('Já existe uma lista com esse nome.');
            } else {
                toast.error(error.response?.data?.error || 'Erro ao criar lista. Tente novamente.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        // Container principal: tela cheia, fundo com imagem, e display flex para dividir em colunas.
        <div
            className="min-h-screen bg-cover bg-center flex"
            style={{ backgroundImage: "url('/assets/fundo.png')" }}
        >
            {/* Sidebar AZUL à esquerda com a cor #15688f */}
            <div
                className="w-1/5 text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen"
            >
                <Link to="/">
                    <img
                        src="/assets/logocogel.jpg" // Caminho da nova logo da COGEL
                        alt="COGEL Logo"
                        className="w-32 h-auto"
                    />
                </Link>
            </div>

            {/* Formulário central (área BRANCA à direita, 4/5 da largura da tela) */}
            <div className="w-4/5 flex items-center justify-center p-8"> {/* Flexbox para centralizar o formulário */}
                <div className="bg-white rounded-lg shadow-md p-10 w-full max-w-2xl"> {/* Conteúdo branco do formulário */}
                    <h1 className="text-2xl font-bold text-black mb-8 text-center">Criar Lista</h1> {/* Centralizado */}

                    <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4"> {/* flex-col para empilhar itens */}
                        <div className="flex-1 w-full"> {/* flex-1 e w-full para input */}
                            <label className="block text-black mb-1">Nome da Lista</label>
                            <input
                                type="text"
                                value={nomeLista}
                                onChange={(e) => setNomeLista(e.target.value)}
                                className="w-full p-2 border rounded text-black" // Adicionado text-black
                                required
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-[#009BE2] cursor-pointer mt-4" // Ajustado mt-4
                            disabled={loading}
                        >
                            {loading ? <ClipLoader size={20} color={"#fff"} /> : 'Criar'}
                        </button>
                    </form>
                </div>
            </div>

            <ToastContainer /> 
        </div>
    );
}

export default CriarLista;