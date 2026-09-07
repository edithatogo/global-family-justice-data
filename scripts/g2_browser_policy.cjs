'use strict';
const crypto = require('node:crypto');
const PLAN = {
  lineage_id: 'G2-ANONYMOUS-BROWSER-20260907-01',
  entry: 'https://www.gov.uk/government/collections/family-court-statistics-quarterly',
  deadline_ms: 900000, max_navigations: 6, max_dashboard_loads: 1,
  max_requests: 300, max_connections: 200, max_encrypted_bytes: 104857600,
  allowed_hosts: ['www.gov.uk', 'assets.publishing.service.gov.uk', 'app.powerbi.com',
    'content.powerapps.com', 'pbivisuals.powerbi.com',
    'wabi-north-europe-e-primary-api.analysis.windows.net',
    'wabi-north-europe-api.analysis.windows.net'],
  blocked_optional_hosts: ['www.googletagmanager.com', 'www.google-analytics.com',
    'dc.services.visualstudio.com', 'browser.events.data.microsoft.com'],
  inherited_session: false, sign_in: false, terms_acceptance: false,
  filter_changes: false, exports: false, manual_api_replay: false,
  raw_response_retention: false, screenshots: false, har: false,
  request_metadata_only: true, g2_acceptance: false,
};
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
function classify(raw, method) {
  let url;
  try { url = new URL(raw); } catch { return {deny: 'url_invalid'}; }
  if (url.protocol !== 'https:' || url.username || url.password || url.port) return {deny: 'url_identity'};
  if (PLAN.blocked_optional_hosts.includes(url.hostname)) return {optional: true};
  if (!PLAN.allowed_hosts.includes(url.hostname)) return {deny: 'destination_denied'};
  let pathname;
  try { pathname = decodeURIComponent(url.pathname); } catch { return {deny: 'path_denied'}; }
  if (/[\\%\u0000-\u001f\u007f]/.test(pathname)) return {deny: 'path_denied'};
  if (/\/(?:login|signin|sign-in|oauth2?|authorize|export|download)(?:[/.;]|$)/i.test(pathname) ||
    /\.(?:pdf|ods|xlsx?|csv|zip|parquet)(?:$|\/)/i.test(pathname)) return {deny: 'path_denied'};
  let category = null;
  if (/\.(?:js|css|png|svg|ico|jpg|jpeg|gif|woff2?|ttf|webp|map)$/i.test(pathname)) category = 'static_asset';
  if (url.hostname === 'www.gov.uk' && pathname.startsWith('/government/')) category = 'official_page';
  if (url.hostname === 'app.powerbi.com' && pathname === '/view') category = 'public_view';
  if (/^\/public\/reports\//.test(pathname) && /\/modelsAndExploration$/.test(pathname)) category = 'models';
  if (/^\/public\/reports\/(?:[a-f0-9-]+\/)?querydata$/i.test(pathname)) category = 'query';
  if (!category) return {deny: 'path_denied'};
  if (!['GET', 'HEAD'].includes(method) && !(['POST', 'OPTIONS'].includes(method) && ['models', 'query'].includes(category))) return {deny: 'method_denied'};
  return {host: url.hostname, category, method, url_sha256: hash(raw)};
}
function requestMetadata(raw, method, headers = {}) {
  const result = classify(raw, method);
  if (result.deny || result.optional) return result;
  const names = Object.keys(headers).map(x => x.toLowerCase());
  if (names.includes('authorization') || names.includes('proxy-authorization')) return {deny: 'authentication_header'};
  return {...result, header_names: names.filter(x => ['x-powerbi-resourcekey', 'content-type', 'origin', 'referer'].includes(x)).sort()};
}
function selectNavigation(links, current, visited) {
  const valid = links.filter(x => !visited.has(x.href) && !classify(x.href, 'GET').deny && !classify(x.href, 'GET').optional);
  const views = [...new Set(valid.filter(x => classify(x.href, 'GET').category === 'public_view').map(x => x.href))];
  if (views.length) return views.length === 1 ? views[0] : null;
  const labelled = [...new Set(valid.filter(x => /dashboard|visuali[sz]ation|data tool/i.test(x.label) && x.href.startsWith('https://www.gov.uk/government/')).map(x => x.href))];
  if (labelled.length) return labelled.length === 1 ? labelled[0] : null;
  const quarter = /\/family-court-statistics-quarterly-(january-to-march|april-to-june|july-to-september|october-to-december)-(20\d{2})$/;
  const seasons = ['january-to-march', 'april-to-june', 'july-to-september', 'october-to-december'];
  const releases = valid.filter(x => x.href.startsWith('https://www.gov.uk/government/statistics/') && quarter.test(x.href))
    .map(x => { const m = x.href.match(quarter); return {url: x.href, period: Number(m[2]) * 4 + seasons.indexOf(m[1])}; });
  if (releases.length && current === PLAN.entry) {
    const newest = Math.max(...releases.map(x => x.period));
    const targets = [...new Set(releases.filter(x => x.period === newest).map(x => x.url))];
    return targets.length === 1 ? targets[0] : null;
  }
  const details = [...new Set(valid.filter(x => x.href.startsWith(current + '/') && /family.court.statistics/i.test(x.label)).map(x => x.href))];
  return details.length === 1 ? details[0] : null;
}
module.exports = {PLAN, hash, classify, requestMetadata, selectNavigation};
