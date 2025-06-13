import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { tenableApiKeysApi, TenableApiKeys } from '../api/backendApi';

function ManageTenableApiKeys() {
    const [accessKey, setAccessKey] = useState('');
    const [secretKey, setSecretKey] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchApiKeys();
    }, []);

    const fetchApiKeys = async () => {
        setLoading(true);
        try {
            // CORREÇÃO: Nome da função corrigido para getTenableApiKeys
            const keys: TenableApiKeys = await tenableApiKeysApi.getTenableApiKeys();
            setAccessKey(keys.TENABLE_ACCESS_KEY || '');
            setSecretKey(keys.TENABLE_SECRET_KEY || '');
            if (!keys.TENABLE_ACCESS_KEY || !keys.TENABLE_SECRET_KEY) {
                toast.warn('As chaves da API Tenable não estão configuradas. Por favor, insira-as.');
            }
        } catch (error) {
            console.error('Erro ao buscar chaves da API Tenable:', error);
            toast.error('Erro ao buscar chaves da API Tenable.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true); // Desabilita o formulário durante o envio
        try {
            await tenableApiKeysApi.updateTenableApiKeys(accessKey, secretKey);
            toast.success('Chaves da API do Tenable atualizadas com sucesso!');
        } catch (error) {
            console.error('Erro ao atualizar chaves da API Tenable:', error);
            toast.error('Erro ao tentar atualizar as chaves da API.');
        } finally {
            setLoading(false); // Habilita o formulário novamente
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

            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md min-h-screen flex flex-col items-center justify-center">
                <div className="bg-gray-100 rounded-lg shadow-md p-10 w-full max-w-2xl">
                    <h1 className="text-2xl font-bold text-gray-800 mb-8 text-center">Gerenciar Chaves da API Tenable</h1>

                    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
                        <div>
                            <label htmlFor="accessKey" className="block text-gray-700 text-sm font-bold mb-2">
                                Access Key:
                            </label>
                            <input
                                type="text"
                                id="accessKey"
                                value={accessKey}
                                onChange={(e) => setAccessKey(e.target.value)}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                disabled={loading}
                                required
                            />
                        </div>

                        <div>
                            <label htmlFor="secretKey" className="block text-gray-700 text-sm font-bold mb-2">
                                Secret Key:
                            </label>
                            <input
                                type="text"
                                id="secretKey"
                                value={secretKey}
                                onChange={(e) => setSecretKey(e.target.value)}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                disabled={loading}
                                required
                            />
                        </div>

                        <div className="flex justify-center mt-4">
                            <button
                                type="submit"
                                className="bg-[#007BB4] text-white px-6 py-2 rounded hover:bg-[#009BE2] cursor-pointer"
                                disabled={loading}
                            >
                                {loading ? <ClipLoader size={20} color={"#fff"} /> : 'Salvar Chaves'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <ToastContainer />
        </div>
    );
}

export default ManageTenableApiKeys;