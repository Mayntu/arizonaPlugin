import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '10s', target: 10 },   // 10 пользователей
        { duration: '10s', target: 100 },  // 100 пользователей
        { duration: '30s', target: 100 },  // 100 пользователей в течении 30 секунд
        { duration: '10s', target: 0 },    // 0 пользователей
    ],
    thresholds: {
        'http_req_duration': ['p(95)<750'], // 95% запросов должны выполняться за 750ms
        'http_req_failed': ['rate<0.05'],   // 5% запросов могут завершиться с ошибкой
    },
};

const BASE_URL = 'http://localhost:5000';

export default function () {
    let tokenResponse = http.post(`${BASE_URL}/token`, JSON.stringify({
        secret: 'arz1528_Tools',
    }), { headers: { 'Content-Type': 'application/json' } });

    check(tokenResponse, { 'status is 201': (r) => r.status === 201 });
    let tokenId = JSON.parse(tokenResponse.body).token_id;

    let validateResponse = http.post(`${BASE_URL}/token/${tokenId}/validate`, JSON.stringify({
        hwid: '123',
    }), { headers: { 'Content-Type': 'application/json' } });

    check(validateResponse, { 'status is 200': (r) => r.status === 200 });

    let captchasResponse = http.post(`${BASE_URL}/get_captchas/${tokenId}`, JSON.stringify({
        hwid: '123',
        zero_chance: 90,
        count: 100,
    }), { headers: { 'Content-Type': 'application/json' } });

    check(captchasResponse, { 'status is 200': (r) => r.status === 200 });

    let calcTaxResponse = http.post(`${BASE_URL}/calc_tax/${tokenId}`, JSON.stringify({
        hwid: '123',
        calcInMskTime: true,
        nalogNow: 50000,
        nalogInHour: 1000,
        property: 'House',
        insurance: true,
        time: 1727467492,
        timeOffset: 3,
      }), { headers: { 'Content-Type': 'application/json' } });

    check(calcTaxResponse, { 'status is 200': (r) => r.status === 200 });

    let searchPropertyResponse = http.post(`${BASE_URL}/search_property/${tokenId}`, JSON.stringify({
        hwid: '123',
        serverNumber : 10,
    }), { headers: { 'Content-Type': 'application/json' } });

    check(searchPropertyResponse, { 'status is 200': (r) => r.status === 200 });

    sleep(1);
}