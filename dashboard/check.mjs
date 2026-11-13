// Offline validation of the shipped aggregate report and its actual calculator functions.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const data = JSON.parse(readFileSync(new URL('data.json', import.meta.url), 'utf8'));
const sum = (rows, key='n') => rows.reduce((s,r)=>s+(r[key]||0),0);
assert.equal(sum(data.daily), 1999232);
assert.equal(sum(data.hourly), sum(data.daily));
assert.equal(sum(data.stations,'departures'), sum(data.daily)-sum(data.daily,'missing_start'));
assert.equal(sum(data.stations,'arrivals'), sum(data.daily)-sum(data.daily,'missing_end'));
for (const [month, expected] of [['202608',645596],['202609',676343],['202610',677293]]) {
 assert.equal(sum(data.daily.filter(r=>r.month===month)), expected);
}
const source = readFileSync(new URL('app.js', import.meta.url),'utf8');
const actualFunctions = source.slice(source.indexOf('function normalCDF('),source.indexOf('function slider('));
const scope = {};
vm.runInNewContext(actualFunctions,scope);
// Reference: statsmodels NormalIndPower and independent normal approximation in Python tests.
assert.equal(scope.powerCalc(70,2,8000).required, 8079);
assert.ok(Math.abs(scope.powerCalc(70,2,4000).power-.5)<.01);
assert.ok(scope.powerCalc(70,2,10000).power>scope.powerCalc(70,2,4000).power);
assert.ok(scope.powerCalc(70,3,8000).required<scope.powerCalc(70,2,8000).required);
assert.equal(data.pilot.snapshots,2);
assert.ok(data.pilot.horizon_seconds<100);
assert.ok(data.simulation.evidence_class.startsWith('SYNTHETIC'));
console.log('Dashboard checks passed: aggregate totals, month cohorts, endpoint denominators, planning reference and evidence labels.');
