// frontend/src/components/MainLayout.tsx

import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header'; // Importa nosso novo Header

const MainLayout: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-grow">
                {/* O <Outlet /> renderiza o componente da rota filha (ex: Scans, Relatorios, etc.) */}
                <Outlet />
            </main>
        </div>
    );
};

export default MainLayout;