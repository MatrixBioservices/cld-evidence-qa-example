"""Mandatory producer evidence contracts. Software assurance only; no scientific policy."""
import re
from datetime import datetime
TEST_VERSION='test-run-p2-1'
PRES_VERSION='preservation-p2-1'
COUNTS={'run','passed','failures','errors','skipped','expected_failures','unexpected_successes'}
TEST_FIELDS={'schema_version','subject_sha256','run_id','started_at','finished_at','returncode','log_path','log_sha256','counts','files_unchanged_during_run','tested_files','command','python'}
PRES_FIELDS={'schema_version','status','changed','removed','added','before_count','after_count','git_status','immutable_snapshot_mismatches','inherited_test_bytes_unchanged','scope','recovery','scientific_validation','release_authorised'}
def sha(v):return isinstance(v,str) and re.fullmatch('[a-f0-9]{64}',v) is not None
def validate_test(t,issue):
 if not isinstance(t,dict) or not TEST_FIELDS.issubset(t):
  issue('TEST_REQUIRED_SCHEMA','Test_Run.json','Required test-run-p2-1 fields missing');return
 if t['schema_version']!=TEST_VERSION:issue('TEST_SCHEMA_VERSION','Test_Run.json','Unsupported producer version')
 if any(not isinstance(t[k],str) or not t[k].strip() for k in ['run_id','started_at','finished_at','log_path','python']):issue('TEST_FIELD_TYPES','Test_Run.json','Nonempty strings required')
 counts=t['counts']
 if not isinstance(counts,dict) or set(counts)!=COUNTS or any(type(counts[k]) is not int or counts[k]<0 for k in COUNTS) or counts['run']<=0:
  issue('TEST_COUNTS_SCHEMA','Test_Run.json','Exact nonnegative integer counts and positive run required')
 else:
  if counts['run']!=sum(counts[k] for k in COUNTS if k!='run'):issue('TEST_COUNTS_TOTAL','Test_Run.json','Denominator mismatch')
  if any(counts[k] for k in COUNTS if k not in {'run','passed'}):issue('TEST_NOT_PASS','Test_Run.json','Producer requires all executed tests to pass')
 try:
  times=[]
  for field in ['started_at','finished_at']:
   if not isinstance(t[field],str):raise ValueError('Timestamp string required')
   value=datetime.fromisoformat(t[field].replace('Z','+00:00'))
   if value.utcoffset() is None:raise ValueError('Timezone required')
   times.append(value)
 except (TypeError,ValueError,OverflowError):
  issue('TEST_TIME_SCHEMA','Test_Run.json','Valid timezone-aware ISO timestamps required')
 else:
  if times[0]>times[1]:issue('TEST_TIME_ORDER','Test_Run.json','Start must not follow finish')
 if not sha(t['subject_sha256']) or not sha(t['log_sha256']):issue('TEST_HASH_SCHEMA','Test_Run.json','SHA256 required')
 if type(t['returncode']) is not int or t['returncode']!=0 or t['files_unchanged_during_run'] is not True:issue('TEST_NOT_PASS','Test_Run.json','Producer execution or custody failed')
 if not isinstance(t['tested_files'],dict) or not t['tested_files'] or any(not isinstance(k,str) or not sha(v) for k,v in t['tested_files'].items()):issue('TEST_FILES_SCHEMA','Test_Run.json','Nonempty tested file digest mapping required')
 if not isinstance(t['command'],list) or not t['command'] or any(not isinstance(v,str) for v in t['command']):issue('TEST_COMMAND_SCHEMA','Test_Run.json','Command array required')
def validate_preservation(p,issue):
 if not isinstance(p,dict) or not PRES_FIELDS.issubset(p):
  issue('PRESERVATION_REQUIRED_SCHEMA','Preservation_Report.json','Required preservation-p2-1 fields missing');return
 if p['schema_version']!=PRES_VERSION:issue('PRESERVATION_SCHEMA_VERSION','Preservation_Report.json','Unsupported producer version')
 for k in ['changed','removed','added','immutable_snapshot_mismatches']:
  if not isinstance(p[k],list) or any(not isinstance(v,str) or not v for v in p[k]):issue('PRESERVATION_LIST_SCHEMA',k,'String list required')
  elif p[k]:issue('PRESERVATION_REQUIRED_FAILURE',k,'Nonempty required failure list contradicts acceptance')
 for k in ['before_count','after_count']:
  if type(p[k]) is not int or p[k]<=0:issue('PRESERVATION_COUNT_SCHEMA',k,'Positive integer required')
 if p['before_count']!=p['after_count']:issue('PRESERVATION_COUNT_TOTAL','Preservation_Report.json','Count mismatch')
 flags=p['inherited_test_bytes_unchanged']
 if not isinstance(flags,dict) or not flags or any(not isinstance(k,str) or not k or type(v) is not bool for k,v in flags.items()):issue('PRESERVATION_FLAGS_SCHEMA','Preservation_Report.json','Nonempty boolean mapping required')
 elif not all(flags.values()):issue('PRESERVATION_INHERITED_FAILURE','Preservation_Report.json','Inherited bytes changed')
 if any(not isinstance(p[k],str) or not p[k].strip() for k in ['scope','recovery']):issue('PRESERVATION_TEXT_SCHEMA','Preservation_Report.json','Scope/recovery required')
 if p['status']!='PASS' or p['git_status']!='PASS' or p['release_authorised'] is not False or p['scientific_validation']!='NOT_PERFORMED':issue('PRESERVATION_NOT_PASS','Preservation_Report.json','Acceptance fields contradict producer contract')
