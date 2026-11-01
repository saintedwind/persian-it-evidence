"""Explicit source routing: internal evidence or uncited model knowledge."""
import json
import re
import time
from evidence import normalize, requests_private_value
import local_answer

GENERAL_SCHEMA={'type':'object','properties':{'answer':{'type':'string'},
    'can_answer':{'type':'boolean'},'needs_live_information':{'type':'boolean'}},
    'required':['answer','can_answer','needs_live_information'],'additionalProperties':False}


def needs_freshness(question):
    q=normalize(question)
    return bool(re.search(r'امروز|اکنون|هم اکنون|در حال حاضر|فعلی|این هفته|این ماه|جدیدترین|آخرین نسخه|آخرین خبر|قیمت روز|خبرهای روز|latest|current|today|2026|1405',q))


def general_answer(question):
    base={'status':'unavailable','answer':None,'answer_source':'none','citations':[],
          'model':local_answer.MODEL,'mode':'model-knowledge','live_web':False}
    if not local_answer.enabled():return base
    if not local_answer.LOCK.acquire(blocking=False):return {**base,'status':'busy'}
    started=time.perf_counter()
    try:
        # Reuse the same bounded loopback transport; no external provider is involved.
        raw=local_answer.request_model(question,None)
        usage=raw.get('usage',{})
        base['usage']={k:usage.get(k,0) for k in ['prompt_tokens','completion_tokens','total_tokens']}
        choice=raw['choices'][0]
        if choice.get('finish_reason')!='stop':return {**base,'status':'incomplete'}
        value=json.loads(choice['message']['content'])
        if (not isinstance(value,dict) or set(value)!={'answer','can_answer','needs_live_information'}
                or type(value['can_answer']) is not bool or type(value['needs_live_information']) is not bool
                or not isinstance(value['answer'],str) or len(value['answer'])>1600):
            return {**base,'status':'invalid_output'}
        if needs_freshness(question) or value['needs_live_information']:
            return {**base,'status':'needs_live_source','freshness_required':True,
                    'model_requested_live_information':value['needs_live_information']}
        if not value['can_answer'] or not value['answer'].strip():return {**base,'status':'insufficient_evidence'}
        if normalize(value['answer']).strip('؟? .\n') == normalize(question).strip('؟? .\n'):
            return {**base,'status':'invalid_output'}
        return {**base,'status':'answer_ready','answer':value['answer'],'answer_source':'model',
                'generation_ms':round((time.perf_counter()-started)*1000,2),
                'notice':'Unverified model knowledge, without internal citation or live web verification.'}
    except (OSError,ValueError,KeyError,IndexError,TypeError):return base
    finally:local_answer.LOCK.release()


def respond(index,question,mode='hybrid'):
    if mode not in ['internal','model','hybrid']:raise ValueError('Unknown answer mode')
    if not isinstance(question,str) or not question.strip() or len(question)>400:raise ValueError('Question must contain 1-400 characters')
    if requests_private_value(question):
        return {'status':'refused','answer':None,'answer_source':'none','citations':[],
                'requested_mode':mode,'reason':'private_credential_request','live_web':False}
    if mode=='model':result=general_answer(question)
    else:
        if needs_freshness(question):
            result={'status':'needs_live_source','answer':None,'citations':[],'answer_source':'none','live_web':False}
        else:
            result=local_answer.answer(index,question)
            result['answer_source']='internal' if result['status']=='answer_ready' else 'none'
        if mode=='hybrid' and result['status'] in ['insufficient_evidence','source_too_long','needs_live_source']:
            reason=result['status']
            result=general_answer(question)
            result['fallback_reason']=reason
    result['requested_mode']=mode
    result.setdefault('answer_source','none');result.setdefault('live_web',False)
    return result
