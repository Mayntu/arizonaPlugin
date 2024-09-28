import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Метрика для отслеживания отказов
export let errorRate = new Rate('errors');

export let options = {
    thresholds: {
        'http_req_duration': ['p(95)<500'], // 95% запросов должны выполняться за 500ms
        'errors': ['rate<0.01'], // Менее 1% запросов должны завершаться с ошибкой
    },
    stages: [
        { duration: '30s', target: 20 },  // 20 пользователей в течение 30 секунд
        { duration: '1m', target: 50 },   // до 50 пользователей за 1 минуту
        { duration: '30s', target: 0 },   // затем уменьшение нагрузки до 0
    ],
};

const BASE_URL = 'http://localhost:5000';  // Базовый URL для вашего FastAPI приложения

export default function () {
    // Тестирование /token
    let tokenResponse = http.post(`${BASE_URL}/token`, JSON.stringify({
        secret: 'arz1528_Tools',
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    check(tokenResponse, {
        'status is 201': (r) => r.status === 201,
        'token is returned': (r) => JSON.parse(r.body).token_id !== undefined,
    });

    let tokenId = JSON.parse(tokenResponse.body).token_id;

    // Тестирование /token/{token_id}/validate
    let validateResponse = http.post(`${BASE_URL}/token/${tokenId}/validate`, JSON.stringify({
        hwid: 'example_hwid',
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    check(validateResponse, {
        'status is 200': (r) => r.status === 200,
        'token is valid': (r) => JSON.parse(r.body).is_valid === true,
    });

    // Тестирование /get_captchas/{token_id}
    let captchasResponse = http.post(`${BASE_URL}/get_captchas/${tokenId}`, JSON.stringify({
        hwid: 'example_hwid',
        zero_chance: 10,
        count: 5,
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    check(captchasResponse, {
        'status is 200': (r) => r.status === 200,
        'captchas returned': (r) => JSON.parse(r.body).captchas.length > 0,
    });

    // Если произошла ошибка, записать в метрику
    if (!validateResponse || !captchasResponse || validateResponse.status !== 200 || captchasResponse.status !== 200) {
        errorRate.add(1);
    } else {
        errorRate.add(0);
    }

    sleep(1); // Пауза между запросами
}
