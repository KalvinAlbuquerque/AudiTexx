// frontend/src/pages/ManageUsers.tsx
import { Link } from 'react-router-dom';
import {  ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function ManageUsers() {
    // ... Implemente a lógica aqui ...
    return (
         <div
            className="flex-grow bg-cover bg-center flex"
            style={{ backgroundImage: "url('/assets/fundo.png')" }}
        >
             <div className="w-1/5 text-white flex flex-col items-center justify-center p-4 shadow-lg">
                <Link to="/"><img src="/assets/logocogel.jpg" alt="COGEL Logo" className="w-32 h-auto" /></Link>
            </div>
            <div className="w-4/5 p-8 bg-white rounded-l-lg shadow-md flex flex-col">
                 <h1 className="text-xl font-bold text-gray-800 mb-4">Gerenciar Usuários (Admin)</h1>
                {/* Aqui viria a UI de gerenciamento */}
                <p>Implementar tabela de usuários e formulário de criação aqui.</p>
            </div>
            <ToastContainer/>
        </div>
    );
}


export default ManageUsers;