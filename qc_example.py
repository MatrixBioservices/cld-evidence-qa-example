"""PROPOSED generic software QC example; artificial records have no biological meaning."""
import argparse,datetime,json,math

def check(records,cutoff):
 """Check record shape, provenance, cutoff availability and explicit eligibility."""
 def time(value):
  if not isinstance(value,str):raise ValueError('timestamp string required')
  result=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
  if result.utcoffset() is None:raise ValueError('timezone required')
  return result
 end=time(cutoff)
 if not isinstance(records,list) or not records:raise ValueError('nonempty record list required')
 findings=[];seen=set();eligible=[]
 for i,row in enumerate(records):
  reasons=[]
  if not isinstance(row,dict):findings.append({'index':i,'reasons':['OBJECT_REQUIRED']});continue
  if row.get('label')!='TEST_FIXTURE':reasons.append('TEST_FIXTURE_REQUIRED')
  rid=row.get('id')
  if not isinstance(rid,str) or not rid:reasons.append('ID_REQUIRED')
  elif rid in seen:reasons.append('DUPLICATE_ID')
  else:seen.add(rid)
  if not isinstance(row.get('source'),str) or not row['source']:reasons.append('SOURCE_REQUIRED')
  try:
   observed,available=time(row.get('observed_at')),time(row.get('available_at'))
   if not observed<=available<=end:reasons.append('CUTOFF_UNAVAILABLE')
  except (TypeError,ValueError):reasons.append('INVALID_TIME')
  if row.get('unit')!='arbitrary_test_unit':reasons.append('UNIT_REQUIRED')
  value=row.get('value')
  if type(value) not in [int,float] or not math.isfinite(value):reasons.append('FINITE_TEST_VALUE_REQUIRED')
  if type(row.get('eligible')) is not bool:reasons.append('EXPLICIT_ELIGIBILITY_REQUIRED')
  if row.get('eligible') is False and (not isinstance(row.get('exclusion_reason'),str) or not row['exclusion_reason']):reasons.append('EXCLUSION_REASON_REQUIRED')
  if reasons:findings.append({'index':i,'reasons':reasons})
  elif row['eligible']:eligible.append(rid)
 return {'status':'FAIL' if findings else 'PASS','registry_records':len(records),'eligible_ids':eligible,'findings':findings,'scientific_interpretation':'NONE_TEST_FIXTURE','release_authorised':False}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('records');ap.add_argument('--cutoff',required=True);a=ap.parse_args()
 try:
  def unique(items):
   d={}
   for k,v in items:
    if k in d:raise ValueError('duplicate JSON key')
    d[k]=v
   return d
  with open(a.records) as stream:records=json.load(stream,object_pairs_hook=unique,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
  result=check(records,a.cutoff)
 except (OSError,ValueError,TypeError,OverflowError) as e:result={'status':'FAIL','error':str(e),'release_authorised':False}
 print(json.dumps(result,allow_nan=False));return 0 if result['status']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
