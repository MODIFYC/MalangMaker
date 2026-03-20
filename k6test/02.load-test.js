import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// 명령어별 응답시간 추적
const writeTrend = new Trend('cmd_write');  // DB 쓰기 발생
const readTrend = new Trend('cmd_read');    // 읽기 전용

export const options = {
  stages: [
    // 1. 평상시 잠잠 (5분)
    { duration: '5m', target: 2 },

    // 2. 갑자기 폭증 (10초만에 50명!)
    { duration: '10s', target: 50 },
    { duration: '1m', target: 50 },   // 50명 유지

    // 3. 다시 잠잠 (15분 대기 → Lambda 컨테이너 내려감)
    { duration: '1m', target: 0 },    // 쿨다운
    { duration: '15m', target: 0 },   // Lambda 대기

    // 4. 콜드 스타트 후 다시 폭증 + 오래 버팀
    { duration: '10s', target: 50 },
    { duration: '10m', target: 50 },  // 10분 버티기
    { duration: '30s', target: 0 },   // 쿨다운
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.05'],
  },
};

const URL = __ENV.MALANG_URL;
if (!URL) throw new Error('MALANG_URL 환경변수를 설정해주세요');

// 읽기 명령어
const readUtterances = ['/상태', '/도움', '/랭킹'];

// 쓰기 명령어 (DynamoDB 쓰기 발생)
const writeUtterances = ['/밥', '/쓰다듬기'];

function makePayload(utterance, userId) {
  return JSON.stringify({
    userRequest: {
      user: {
        id: userId,
        properties: { nickname: '테스터' }
      },
      utterance: utterance,
      chatRoom: { id: `test_room_${Math.floor(Math.random() * 5)}` }
    }
  });
}

export default function () {
  const userId = `test_user_${Math.floor(Math.random() * 30)}`;
  const params = { headers: { 'Content-Type': 'application/json' } };

  // 70% 읽기 / 30% 쓰기 (실제 사용 패턴 비슷하게)
  if (Math.random() < 0.7) {
    const utterance = readUtterances[Math.floor(Math.random() * readUtterances.length)];
    const res = http.post(URL, makePayload(utterance, userId), params);
    readTrend.add(res.timings.duration);
    check(res, {
      '[읽기] 응답 200': (r) => r.status === 200,
      '[읽기] 3초 이내': (r) => r.timings.duration < 3000,
    });
  } else {
    const utterance = writeUtterances[Math.floor(Math.random() * writeUtterances.length)];
    const res = http.post(URL, makePayload(utterance, userId), params);
    writeTrend.add(res.timings.duration);
    check(res, {
      '[쓰기] 응답 200': (r) => r.status === 200,
      '[쓰기] 3초 이내': (r) => r.timings.duration < 3000,
    });
  }

  sleep(1);
}

// ===============결과===================

//   █ THRESHOLDS

//     http_req_duration
//     ✓ 'p(95)<3000' p(95)=63.84ms

//     http_req_failed
//     ✗ 'rate<0.05' rate=6.62%


//   █ TOTAL RESULTS

//     checks_total.......: 69064  35.040487/s
//     checks_succeeded...: 96.68% 66775 out of 69064
//     checks_failed......: 3.31%  2289 out of 69064

//     ✗ [읽기] 응답 200
//       ↳  92% — ✓ 22430 / ✗ 1729
//     ✓ [읽기] 3초 이내
//     ✗ [쓰기] 응답 200
//       ↳  94% — ✓ 9813 / ✗ 560
//     ✓ [쓰기] 3초 이내

//     CUSTOM
//     cmd_read.......................: avg=45.364026 min=19.1289 med=43.549  max=1528.9642 p(90)=56.61942 p(95)=63.32862
//     cmd_write......................: avg=46.246534 min=16.9296 med=42.5788 max=1390.1805 p(90)=58.75826 p(95)=64.58424

//     HTTP
//     http_req_duration..............: avg=45.62ms   min=16.92ms med=43.29ms max=1.52s     p(90)=57.27ms  p(95)=63.84ms
//       { expected_response:true }...: avg=45.37ms   min=24.95ms med=42.98ms max=1.52s     p(90)=57.09ms  p(95)=63.5ms
//     http_req_failed................: 6.62%  2289 out of 34532
//     http_reqs......................: 34532  17.520244/s

//     EXECUTION
//     iteration_duration.............: avg=1.04s     min=1.01s   med=1.04s   max=2.6s      p(90)=1.05s    p(95)=1.06s
//     iterations.....................: 34532  17.520244/s
//     vus............................: 2      min=0             max=50
//     vus_max........................: 50     min=50            max=50

//     NETWORK
//     data_received..................: 48 MB  24 kB/s
//     data_sent......................: 7.6 MB 3.8 kB/s



                                                                                                                                     
// running (32m51.0s), 00/50 VUs, 34532 complete and 0 interrupted iterations                                                           
// default ✓ [======================================] 00/50 VUs  32m50s                                                                 
// ERRO[1971] thresholds on metrics 'http_req_failed' have been crossed