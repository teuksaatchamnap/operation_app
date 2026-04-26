import { createRouter, createWebHistory } from 'vue-router';

const pageModules = import.meta.glob('../pages/**/*.vue');

function generateRoutes() {
    const routes = [];

    for (const filePath of Object.keys(pageModules)) {
        const fileName = filePath.split('/').pop().replace(/\.\w+$/, '');
        let path = '/' + fileName.toLowerCase();

        if (fileName === 'Index') {
            path = '/';
        }

        routes.push({
            path,
            name: fileName,
            component: pageModules[filePath],
        });
    }

    routes.sort((a, b) => {
        if (a.path === '/') return 1;
        if (b.path === '/') return -1;
        return a.path.localeCompare(b.path);
    });

    return routes;
}

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/login' },
        ...generateRoutes(),
    ],
});

export default router;
