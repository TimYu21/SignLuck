import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
});

export const getCheck = (userQuery) => {
    return api.post('/check', { query: userQuery });
};