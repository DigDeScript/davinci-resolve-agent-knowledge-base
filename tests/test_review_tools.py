"""Offline safety/meaning tests; actual Resolve integration evidence is separate."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from resolve_inspect import compare, differences, write_json
from review_frames import cut_frames, parse_frames
import uuid

def snapshot():
    return {'schema_version':'resolve-inspect/1','read_errors':[],
            'state':{'media':[{'properties':{'Usage':'1','Resolution':'1920x1080'}}],
                     'timelines':[{'tracks':[{'items':[{'fades':{'FadeOut':8},
                                   'properties':{'AudioVolume':-3},'links':['pair']}]}]}]}}

class Item:
    def __init__(self,start,end,kind='video'):self.start,self.end,self.kind=start,end,kind
    def GetStart(self):return self.start
    def GetEnd(self):return self.end
    def GetType(self):return self.kind

class Timeline:
    def GetStartFrame(self):return 108000
    def GetItemListInTrack(self,kind,index):
        return [Item(108025,108030,'transition'),Item(108040,108060),Item(108000,108030)]

class ReviewTests(unittest.TestCase):
    def test_detects_lost_fade_and_gain(self):
        a=snapshot();b=copy.deepcopy(a)
        item=b['state']['timelines'][0]['tracks'][0]['items'][0]
        item['fades']['FadeOut']=0;item['properties']['AudioVolume']=-9
        result=compare(a,b)
        self.assertFalse(result['equal']);self.assertEqual(len(result['changes']),2)

    def test_unknown_is_not_success(self):
        a=snapshot();a['read_errors']=[{'method':'GetFades','error':'unavailable'}]
        self.assertEqual(compare(a,a)['status'],'incomplete')

    def test_usage_is_separate_but_resolution_is_not(self):
        a=snapshot();b=copy.deepcopy(a);b['state']['media'][0]['properties']['Usage']='0'
        result=compare(a,b);self.assertTrue(result['equal']);self.assertEqual(len(result['observations']),1)
        b['state']['media'][0]['properties']['Resolution']='0x0'
        self.assertFalse(compare(a,b)['equal'])

    def test_missing_field_is_not_equal_to_null(self):
        self.assertTrue(differences({}, {'gain':None}))

    def test_cut_offsets_preserve_actual_gap_and_ignore_transition(self):
        self.assertEqual([x['frameOffset'] for x in cut_frames(Timeline(),1)],[29,40])

    def test_negative_frame_rejected(self):
        with self.assertRaises(ValueError):parse_frames('0,-1')

    def test_previous_evidence_not_overwritten(self):
        test_root=Path(__file__).resolve().parent
        path=test_root/('qa_test_'+uuid.uuid4().hex+'.json')
        try:
            write_json(path,{'old':True})
            with self.assertRaises(FileExistsError):write_json(path,{'old':False})
        finally:
            if path.exists():path.unlink()

if __name__=='__main__':unittest.main()
