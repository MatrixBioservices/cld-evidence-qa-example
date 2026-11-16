"""Portable software tests: every input is an artificial TEST_FIXTURE."""
import sys,json,copy,unittest,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from qc_example import check
from mandatory_evidence import validate_test,validate_preservation
CUTOFF='2026-01-03T00:00:00+00:00'
def records():return json.loads((ROOT/'fixtures/TEST_FIXTURE_records.json').read_text())

def test_envelope():
 """Invented producer declaration; does not attest any real execution."""
 return {
  'schema_version':'test-run-p2-1','subject_sha256':'a'*64,
  'run_id':'TEST_FIXTURE_RUN','started_at':'2026-01-01T00:00:00+00:00',
  'finished_at':'2026-01-01T00:00:01+00:00','returncode':0,
  'log_path':'TEST_FIXTURE.log','log_sha256':'b'*64,
  'counts':{'run':2,'passed':2,'failures':0,'errors':0,'skipped':0,
            'expected_failures':0,'unexpected_successes':0},
  'files_unchanged_during_run':True,'tested_files':{'TEST_FIXTURE.py':'c'*64},
  'command':['TEST_FIXTURE'],'python':'TEST_FIXTURE_PYTHON'
 }

def envelope_codes(envelope):
 findings=[]
 validate_test(envelope,lambda code,*details:findings.append(code))
 return findings

class EvidenceContractTests(unittest.TestCase):
 def test_valid_declaration(self):
  self.assertEqual(envelope_codes(test_envelope()),[])
 def test_counts_null_or_nonobject(self):
  for value in [None,[],0,'2']:
   with self.subTest(value=value):
    t=test_envelope();t['counts']=value
    self.assertIn('TEST_COUNTS_SCHEMA',envelope_codes(t))
 def test_counts_exact_keys(self):
  for mode in ['missing','extra']:
   with self.subTest(mode=mode):
    t=test_envelope()
    if mode=='missing':t['counts'].pop('skipped')
    else:t['counts']['other']=0
    self.assertIn('TEST_COUNTS_SCHEMA',envelope_codes(t))
 def test_counts_nonnegative_integers(self):
  for key in test_envelope()['counts']:
   for value in [True,False,-1,1.0,'1',None]:
    with self.subTest(key=key,value=value):
     t=test_envelope();t['counts'][key]=value
     self.assertIn('TEST_COUNTS_SCHEMA',envelope_codes(t))
 def test_counts_run_positive(self):
  t=test_envelope();t['counts'].update(run=0,passed=0)
  self.assertIn('TEST_COUNTS_SCHEMA',envelope_codes(t))
 def test_counts_reconcile(self):
  for passed in [1,3]:
   with self.subTest(passed=passed):
    t=test_envelope();t['counts']['passed']=passed
    self.assertIn('TEST_COUNTS_TOTAL',envelope_codes(t))
 def test_nonpassing_categories_rejected(self):
  for key in ['failures','errors','skipped','expected_failures','unexpected_successes']:
   with self.subTest(key=key):
    t=test_envelope();t['counts'][key]=1;t['counts']['passed']=1
    codes=envelope_codes(t)
    self.assertIn('TEST_NOT_PASS',codes);self.assertNotIn('TEST_COUNTS_TOTAL',codes)
 def test_invalid_calendar_and_timestamp_values(self):
  for field in ['started_at','finished_at']:
   for value in ['not-a-date','2026-02-30T00:00:00+00:00','2026-13-01T00:00:00Z','',None,42]:
    with self.subTest(field=field,value=value):
     t=test_envelope();t[field]=value
     self.assertIn('TEST_TIME_SCHEMA',envelope_codes(t))
 def test_timezone_required(self):
  for field in ['started_at','finished_at']:
   for value in ['2026-01-01','2026-01-01T00:00:00']:
    with self.subTest(field=field,value=value):
     t=test_envelope();t[field]=value
     self.assertIn('TEST_TIME_SCHEMA',envelope_codes(t))
 def test_reverse_time_rejected(self):
  t=test_envelope();t['started_at']='2026-01-01T00:00:02Z'
  self.assertIn('TEST_TIME_ORDER',envelope_codes(t))
 def test_z_and_offset_order_positive(self):
  t=test_envelope();t['started_at']='2026-01-01T09:00:00+09:00';t['finished_at']='2026-01-01T00:00:01Z'
  self.assertEqual(envelope_codes(t),[])
 def test_equal_timestamps_allowed(self):
  t=test_envelope();t['finished_at']=t['started_at']
  self.assertEqual(envelope_codes(t),[])
 def test_no_untrusted_wall_clock_freshness_rule(self):
  for year in ['2000','2099']:
   with self.subTest(year=year):
    t=test_envelope();t['started_at']=year+'-01-01T00:00:00Z';t['finished_at']=year+'-01-01T00:00:01Z'
    self.assertEqual(envelope_codes(t),[])
 def test_nonzero_returncode_still_rejected(self):
  t=test_envelope();t['returncode']=2
  self.assertIn('TEST_NOT_PASS',envelope_codes(t))
 def test_cli_invalid_dates_exit_two(self):
  for invalid_cutoff in [False,True]:
   with self.subTest(invalid_cutoff=invalid_cutoff),tempfile.TemporaryDirectory() as tmp:
    rows=records();cutoff=CUTOFF
    if invalid_cutoff:cutoff='invalid-date'
    else:rows[0]['available_at']='2026-02-30T00:00:00Z'
    path=Path(tmp)/'TEST_FIXTURE.json';path.write_text(json.dumps(rows))
    result=subprocess.run([sys.executable,'-B',str(ROOT/'qc_example.py'),str(path),'--cutoff',cutoff],capture_output=True,text=True)
    self.assertEqual(result.returncode,2);self.assertEqual(json.loads(result.stdout)['status'],'FAIL')

class ExampleTests(unittest.TestCase):
 def test_valid_and_exclusion(self):
  result=check(records(),CUTOFF);self.assertEqual(result['status'],'PASS');self.assertEqual(result['registry_records'],2);self.assertEqual(result['eligible_ids'],['TEST_A']);self.assertFalse(result['release_authorised'])
 def test_cutoff(self):
  rows=records();rows[0]['available_at']='2026-01-04T00:00:00+00:00';self.assertEqual(check(rows,CUTOFF)['status'],'FAIL')
 def test_missing_provenance(self):
  rows=records();rows[0].pop('source');self.assertEqual(check(rows,CUTOFF)['status'],'FAIL')
 def test_duplicate(self):self.assertEqual(check(records()*2,CUTOFF)['status'],'FAIL')
 def test_invalid_never_eligible(self):
  rows=records();rows[0]['value']=None;self.assertEqual(check(rows,CUTOFF)['eligible_ids'],[])
 def test_boolean_not_numeric(self):
  rows=records();rows[0]['value']=True;self.assertEqual(check(rows,CUTOFF)['status'],'FAIL')
 def test_mandatory_empty(self):
  for validator in [validate_test,validate_preservation]:
   findings=[];validator({},lambda *x:findings.append(x));self.assertTrue(findings)
 def test_actual_cli(self):
  p=subprocess.run([sys.executable,'-B',str(ROOT/'qc_example.py'),str(ROOT/'fixtures/TEST_FIXTURE_records.json'),'--cutoff',CUTOFF],capture_output=True,text=True,cwd=ROOT);self.assertEqual(p.returncode,0);self.assertFalse(json.loads(p.stdout)['release_authorised'])
 def test_actual_cli_invalid(self):
  with tempfile.TemporaryDirectory() as tmp:
   pth=Path(tmp)/'TEST_FIXTURE.json';pth.write_text('{}');p=subprocess.run([sys.executable,'-B',str(ROOT/'qc_example.py'),str(pth),'--cutoff',CUTOFF],capture_output=True,text=True);self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['status'],'FAIL')
