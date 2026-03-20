import http from 'k6/http';
import { check, sleep } from 'k6';

// 부하 테스트 시나리오
export const options = {
    stages: [
        { duration: '30s', target: 5 },   // 30초 동안 5명으로 증가
        { duration: '1m', target: 5 },   // 1분 동안 5명 유지
        { duration: '30s', target: 10 },  // 30초 동안 10명으로 증가
        { duration: '1m', target: 10 },  // 1분 동안 10명 유지
        { duration: '30s', target: 0 },   // 30초 동안 0으로 감소
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'],  // 95%가 3초 이내
        http_req_failed: ['rate<0.05'],     // 에러율 5% 미만
    },
};

const URL = 'https://b99hylu2el.execute-api.ap-northeast-2.amazonaws.com/Prod/message';

// 테스트할 명령어 목록
const utterances = [
    '/상태',
    '/밥',
    '/도움',
    '/랭킹',
];

export default function () {
    // 랜덤 유저 ID (동시 사용자 시뮬레이션)
    const userId = `test_user_${Math.floor(Math.random() * 20)}`;
    const utterance = utterances[Math.floor(Math.random() * utterances.length)];

    const payload = JSON.stringify({
        userRequest: {
            user: {
                id: userId,
                properties: {
                    nickname: '테스터'
                }
            },
            utterance: utterance,
            chatRoom: {
                id: `test_room_${Math.floor(Math.random() * 5)}`
            }
        }
    });

    const params = {
        headers: { 'Content-Type': 'application/json' },
    };

    const res = http.post(URL, payload, params);

    check(res, {
        '응답 200': (r) => r.status === 200,
        '응답시간 3초 이내': (r) => r.timings.duration < 3000,
    });

    sleep(1);
}


// ===============결과===================
// █ THRESHOLDS

//     http_req_duration
//     ✓ 'p(95)<3000' p(95)=66.97ms

//     http_req_failed
//     ✓ 'rate<0.05' rate=0.00%


//   █ TOTAL RESULTS

//     checks_total.......: 2578    12.23133/s
//     checks_succeeded...: 100.00% 2578 out of 2578
//     checks_failed......: 0.00%   0 out of 2578

//     ✓ 응답 200
//     ✓ 응답시간 3초 이내

//     HTTP
//     http_req_duration..............: avg=49.83ms min=27.81ms med=47.68ms max=1.86s p(90)=59.72ms p(95)=66.97ms
//       { expected_response:true }...: avg=49.83ms min=27.81ms med=47.68ms max=1.86s p(90)=59.72ms p(95)=66.97ms
//     http_req_failed................: 0.00%  0 out of 1289
//     http_reqs......................: 1289   6.115665/s

//     EXECUTION
//     iteration_duration.............: avg=1.05s   min=1.02s   med=1.04s   max=2.96s p(90)=1.06s   p(95)=1.07s
//     iterations.....................: 1289   6.115665/s
//     vus............................: 1      min=1         max=10
//     vus_max........................: 10     min=10        max=10

//     NETWORK
//     data_received..................: 1.8 MB 8.7 kB/s
//     data_sent......................: 293 kB 1.4 kB/s



                                                                                                                                     
// running (3m30.8s), 00/10 VUs, 1289 complete and 0 interrupted iterations   