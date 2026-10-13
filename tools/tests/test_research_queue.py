import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import research_queue as queue
import research_runtime as runtime


FAKE_CODEX = r'''
import json,sys,time
from pathlib import Path
if '--version' in sys.argv:
    print('codex-cli fixture'); raise SystemExit(0)
if '--help' in sys.argv:
    print('--output-schema --add-dir --json'); raise SystemExit(0)
if 'login' in sys.argv:
    raise SystemExit(0)
destination=Path(sys.argv[sys.argv.index('--output-last-message')+1])
round_dir=destination.parent
directory=round_dir.parents[2]
root=Path(__file__).parent
state=json.loads((directory/'state.json').read_text(encoding='utf-8'))
task=json.loads((root/'items'/directory.name/'task.json').read_text(encoding='utf-8'))
mode=task.get('fixture_mode','two-rounds')
prompt=sys.stdin.read()
assert str(round_dir/'RESEARCH_PACKET.md') in prompt
if mode=='fail':
    print('fixture failure',file=sys.stderr); raise SystemExit(7)
if mode=='timeout': time.sleep(30)
if mode=='slow': time.sleep(0.4)
packet=json.loads((round_dir/'PACKET.json').read_text(encoding='utf-8'))
evidence=round_dir/'artifacts/check.log'
evidence.write_text('fixture check passed; previous next_action='+state['next_action'],encoding='utf-8')
ref='workspace:'+evidence.relative_to(root).as_posix()
status='completed' if state['attempts']>=2 or mode in ('complete','slow','bad-completion') else 'continue'
if mode=='experiment':
    import subprocess
    subprocess.run([sys.executable,'-B',task['fixture_helper'],'--config',str(round_dir/'EXPERIMENT_CONFIG.json'),'run','tiny'],check=True)
    status='completed'
if mode=='blocked': status='blocked'
if mode=='waiting': status='waiting'
if mode=='no-progress': status='continue'
if mode=='stop' and state['attempts']==1:
    (root/'control/STOP').write_text('boundary stop',encoding='utf-8')
if mode=='conflict':
    (directory/'progress.md').write_text('external edit to preserve',encoding='utf-8')
if mode=='edit-task':
    task['objective']='Changed while worker was active'
    (root/'items'/directory.name/'task.json').write_text(json.dumps(task),encoding='utf-8')
value={'schema_version':1,**packet,'status':status,'next_phase':'assess','progress_made':mode!='no-progress',
       'summary':'fixture round '+str(state['attempts']),'next_action':'continue-from-round-'+str(state['attempts']),
       'current_state':'# Fixture state\nNext: continue-from-round-'+str(state['attempts']),
       'blocker':'fixture external prerequisite' if status in ('blocked','waiting') else '',
       'evidence':[ref],'checks':[{'command':'fixture assertion','exit_code':0,'log':ref}],
       'acceptance':[{'id':c['id'],'outcome':'not-run' if mode=='bad-completion' else 'passed','evidence':[ref]} for c in task['acceptance']]}
if mode=='wrong-hash': value['packet_sha256']='wrong'
if mode=='missing-evidence': value['evidence']=['workspace:missing.txt']
if mode=='malformed': value['checks']=['invalid']
destination.write_text(json.dumps(value),encoding='utf-8')
print(json.dumps({'type':'thread.started','thread_id':'fixture-thread'}))
print(json.dumps({'type':'item.started','item':{'type':'command_execution','id':'one'}}))
print(json.dumps({'type':'item.completed','item':{'type':'command_execution','id':'one'}}))
if mode!='no-usage':
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':11,'cached_input_tokens':7,'output_tokens':3}}))
'''


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'agent space'
        self.root.mkdir()
        self.project = self.root.parent / 'PDE \u5fc3\u810f project'
        (self.project / 'code').mkdir(parents=True)
        (self.project / 'code/main.py').write_text('value = 1\n', encoding='utf-8')
        self.worker = self.root / 'fixture_codex.py'
        self.worker.write_text(FAKE_CODEX, encoding='utf-8')
        self.config_path = self.root / 'research-queue.json'
        settings = {'schema_version':1,'workspace_config':'cardiac-workspace.json','items_dir':'items',
                    'state_dir':'states','runtime_dir':'control','codex_command':[sys.executable,'-B',str(self.worker)],
                    'max_rounds':8,'max_wall_hours':0.02,'round_timeout_minutes':0.1,'poll_seconds':0.01,
                    'idle_seconds':0.01,'max_consecutive_runtime_failures':1,'max_no_progress_rounds':2}
        runtime.write_json(self.config_path, settings)
        runtime.write_json(self.root/'cardiac-workspace.json', {'schema_version':1,'project_root':'../'+self.project.name,
                           'data_dir':'data','runs_dir':'runs','tasks':{},'source_roots':['code']})
        for name in ['AGENTS.md','agents/core/research-core.md','agents/core/queue-core.md','agents/protocols/round-result.md',
                     'projects/cardiac-ep/problem.md','projects/cardiac-ep/CURRENT_STATE.md','projects/cardiac-ep/claim-map.md',
                     'projects/cardiac-ep/SOURCE_MAP.md'] + [f'agents/protocols/{n}.md' for n in ['explore','computation','data-validation','model-validation']]:
            path=self.root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text('# Fixture context\nNo scientific claims.\n',encoding='utf-8')
        self.config=queue.load_config(self.config_path)
        self.add_task('alpha')

    def add_task(self,slug,mode='two-rounds',**options):
        task={'slug':slug,'title':slug,'objective':'Complete the fixture objective','scope':'Temporary fixture only',
              'ready':True,'enabled':True,'priority':0,'max_rounds':0,'acceptance':[{'id':'C1','description':'Fixture output exists'}],
              'fixture_mode':mode,**options}
        runtime.write_json(queue.task_file(self.config,slug),task)
        return task

    def run_loop(self,**kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return queue.run_loop(self.config,**kwargs)

    def state(self,slug='alpha'):
        return queue.read_state(self.config,queue.read_task(queue.task_file(self.config,slug)))

    def cli(self,*args):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return queue.main(['--config',str(self.config_path),*args])

    def test_two_rounds_follow_previous_result_and_finish(self):
        self.assertEqual(self.run_loop(),0)
        state=self.state()
        self.assertEqual((state['status'],state['attempts']),('completed',2))
        directory=queue.task_directory(self.config,'alpha')
        last=directory/'.runtime/rounds'/state['last_round']
        self.assertIn('continue-from-round-1',(last/'artifacts/check.log').read_text())
        self.assertTrue((last/'APPLIED.json').exists())
        self.assertEqual((state['input_tokens'],state['output_tokens']),(22,6))
        self.assertEqual(runtime.read_json(last/'RUN.json')['usage']['tool_calls'],1)
        self.assertEqual((self.project/'code/main.py').read_text(),'value = 1\n')

    def test_launch_budget_preserves_state_for_next_launch(self):
        self.config['max_rounds']=1
        self.run_loop()
        self.assertEqual(self.state()['status'],'pushing')
        self.assertEqual(runtime.read_json(self.root/'control/RUNNER.json')['status'],'budget-exhausted')
        self.run_loop()
        self.assertEqual((self.state()['attempts'],self.state()['status']),(2,'completed'))

    def test_completed_task_does_not_freeze_another_task(self):
        self.add_task('alpha','complete')
        self.add_task('beta','complete')
        self.run_loop()
        self.assertEqual(self.state('alpha')['status'],'completed')
        self.assertEqual(self.state('beta')['status'],'completed')

    def test_round_robin_is_fair(self):
        self.add_task('beta')
        self.config['max_rounds']=2
        self.run_loop()
        self.assertEqual((self.state('alpha')['attempts'],self.state('beta')['attempts']),(1,1))

    def test_failure_blocks_only_affected_task(self):
        self.add_task('alpha','fail')
        self.add_task('beta','complete')
        self.run_loop()
        self.assertEqual(self.state('alpha')['status'],'runtime-error')
        self.assertEqual(self.state('beta')['status'],'completed')
        self.assertEqual(self.state('alpha')['last_exit_code'],7)

    def test_invalid_results_never_mark_task_completed(self):
        for mode in ['bad-completion','wrong-hash','missing-evidence','malformed']:
            with self.subTest(mode=mode):
                slug=mode
                self.add_task(slug,mode)
                self.assertEqual(self.run_loop(slug=slug),1)
                self.assertEqual(self.state(slug)['status'],'runtime-error')

    def test_stop_is_honored_at_round_boundary_and_can_restart(self):
        self.add_task('alpha','stop')
        self.run_loop()
        self.assertEqual(self.state()['attempts'],1)
        self.assertEqual(runtime.read_json(self.root/'control/RUNNER.json')['status'],'stopped')
        self.run_loop()
        self.assertEqual(self.state()['status'],'completed')

    def test_dry_run_is_read_only_and_keeps_pending_stop(self):
        runtime.atomic(self.root/'control/STOP',b'stop')
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.run_loop(dry_run=True)
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.run_loop()
        self.assertEqual(self.state()['attempts'],0)

    def test_timeout_is_a_failed_round_with_saved_logs(self):
        self.add_task('alpha','timeout')
        self.config['round_timeout_minutes']=0.01
        started=time.monotonic()
        self.assertEqual(self.run_loop(),1)
        self.assertLess(time.monotonic()-started,8)
        self.assertEqual((self.state()['status'],self.state()['last_exit_code']),('runtime-error',124))

    def test_total_wall_budget_limits_current_round(self):
        self.add_task('alpha','timeout')
        self.config['max_wall_hours']=0.00005
        self.run_loop()
        state=self.state()
        record=runtime.read_json(queue.task_directory(self.config,'alpha')/'.runtime/rounds'/state['last_round']/'RUN.json')
        self.assertLessEqual(record['timeout_seconds'],0.18)

    def test_missing_usage_stops_token_budget_instead_of_assuming_zero(self):
        self.add_task('alpha','no-usage')
        self.config['max_tokens']=100
        self.assertEqual(self.run_loop(),1)
        self.assertEqual(self.state()['attempts'],1)
        self.assertEqual(runtime.read_json(self.root/'control/RUNNER.json')['status'],'usage-unavailable')

    def test_token_budget_counts_input_plus_output_without_double_cached(self):
        self.config['max_tokens']=14
        self.run_loop()
        record=runtime.read_json(self.root/'control/RUNNER.json')
        self.assertEqual((record['tokens'],record['rounds'],record['status']),(14,1,'budget-exhausted'))

    def test_no_progress_and_waiting_have_distinct_behavior(self):
        self.add_task('alpha','no-progress')
        self.run_loop()
        self.assertEqual((self.state()['attempts'],self.state()['status']),(2,'blocked'))
        self.add_task('beta','waiting')
        self.run_loop(slug='beta',once=True)
        self.assertEqual(self.state('beta')['status'],'waiting')
        self.assertEqual(self.state('beta')['no_progress'],0)
        self.assertGreater(self.state('beta')['not_before'],0)

    def test_concurrent_state_edit_is_preserved_and_pauses_task(self):
        self.add_task('alpha','conflict')
        self.run_loop()
        directory=queue.task_directory(self.config,'alpha')
        self.assertEqual((directory/'progress.md').read_text(),'external edit to preserve')
        self.assertEqual(self.state()['status'],'runtime-error')
        self.assertEqual(self.state()['attempts'],1)

    def test_interrupted_uncommitted_round_needs_explicit_resume(self):
        task=queue.read_task(queue.task_file(self.config,'alpha'))
        directory=queue.task_directory(self.config,'alpha')
        runtime.initialize(directory,task)
        state=self.state()
        state.update(active_round='unfinished',attempts=1,status='pushing')
        runtime.write_json(directory/'state.json',state)
        self.run_loop()
        self.assertEqual(self.state()['status'],'runtime-error')
        self.assertEqual(self.cli('resume','alpha'),0)
        self.run_loop()
        self.assertEqual((self.state()['status'],self.state()['attempts']),('completed',2))

    def test_partial_commit_recovers_without_duplicate_history(self):
        self.add_task('alpha','complete')
        real_recover=runtime.recover
        interrupted=[False]
        def crash_once(directory,round_dir):
            if not interrupted[0]:
                interrupted[0]=True
                runtime.atomic(directory/'state.json',(round_dir/'after/state.json').read_bytes())
                raise OSError('simulated interruption')
            return real_recover(directory,round_dir)
        with patch.object(runtime,'recover',side_effect=crash_once):
            self.assertEqual(self.run_loop(),0)
        self.assertEqual(self.state()['status'],'completed')
        directory=queue.task_directory(self.config,'alpha')
        self.assertEqual((directory/'progress.md').read_text().count('fixture round 1'),1)
        self.run_loop()
        self.assertEqual(self.state()['attempts'],1)

    def test_workspace_lock_prevents_two_writers(self):
        with runtime.lock(self.root/'control/runner.lock'):
            self.assertTrue(runtime.locked(self.root/'control/runner.lock'))
            self.assertEqual(self.cli('once'),1)
        self.assertFalse(runtime.locked(self.root/'control/runner.lock'))

    def test_new_tasks_can_be_added_and_enabled_during_a_run(self):
        with runtime.lock(self.root/'control/runner.lock'):
            self.assertEqual(self.cli('add','beta','New study','--objective','Fixture task','--criterion','Fixture evidence'),0)
            self.assertFalse(queue.read_task(queue.task_file(self.config,'beta'))['ready'])
            self.assertEqual(self.cli('enable','beta'),0)
            self.assertTrue(queue.read_task(queue.task_file(self.config,'beta'))['ready'])
            self.assertEqual(self.cli('pause','alpha'),1)

    def test_task_definition_change_pauses_without_retrying_changed_goal(self):
        self.add_task('alpha','edit-task')
        self.config['max_consecutive_runtime_failures']=3
        self.run_loop()
        self.assertEqual((self.state()['status'],self.state()['attempts']),('runtime-error',1))

    def test_oversized_task_packet_does_not_freeze_other_tasks(self):
        task=queue.read_task(queue.task_file(self.config,'alpha'))
        directory=queue.task_directory(self.config,'alpha')
        runtime.initialize(directory,task)
        (directory/'CURRENT_STATE.md').write_text('x'*13000,encoding='utf-8')
        self.add_task('beta','complete')
        self.run_loop()
        self.assertEqual(self.state('alpha')['status'],'runtime-error')
        self.assertEqual(self.state('beta')['status'],'completed')
        self.assertTrue((directory/'PREPARATION_ERROR.json').exists())

    def test_worker_runs_experiment_helper_inside_its_writable_task_directory(self):
        workspace_path=self.root/'cardiac-workspace.json'
        config=runtime.read_json(workspace_path)
        config['tasks']={'tiny':{'cwd':'code','argv':['{python}','-c','print("experiment fixture passed")'],
                                 'timeout_seconds':5,'requires_data':False}}
        runtime.write_json(workspace_path,config)
        self.config=queue.load_config(self.config_path)
        self.add_task('alpha','experiment',fixture_helper=str(queue.ROOT/'tools/cardiac_workspace.py'))
        self.assertEqual(self.run_loop(),0)
        directory=queue.task_directory(self.config,'alpha')
        results=list(directory.glob('.runtime/rounds/*/artifacts/experiments/*/run.json'))
        self.assertEqual(len(results),1)
        result=runtime.read_json(results[0])
        self.assertEqual((result['status'],result['exit_code']),('completed',0))
        self.assertEqual(result['cwd'],str(self.project/'code'))
        self.assertFalse((self.root/'runs').exists())

    def test_task_lifetime_round_limit_survives_new_launches(self):
        self.add_task('alpha',max_rounds=1)
        self.run_loop()
        self.run_loop()
        self.assertEqual(self.state()['attempts'],1)

    def test_packet_preview_needs_no_task_initialization(self):
        self.assertEqual(self.cli('packet','alpha'),0)
        self.assertFalse((self.root/'states').exists())

    def test_command_keeps_sandbox_and_inherits_model(self):
        plan=queue.preview(self.config,queue.read_task(queue.task_file(self.config,'alpha')))
        argv=plan['argv']
        self.assertIn('workspace-write',argv)
        self.assertIn('--output-schema',argv)
        self.assertIn('--add-dir',argv)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',argv)
        self.assertNotIn('-m',argv)

    def test_evidence_cannot_escape_workspace(self):
        outside=self.root.parent/'outside.txt'
        outside.write_text('outside')
        with self.assertRaises(ValueError):
            runtime.evidence_file('workspace:../outside.txt',self.root,self.project)

    def test_background_start_finishes_and_releases_lock(self):
        self.add_task('alpha','slow')
        self.assertEqual(self.cli('start','--slug','alpha','--max-rounds','1'),0)
        deadline=time.monotonic()+10
        record=self.root/'control/RUNNER.json'
        while time.monotonic()<deadline:
            if record.exists() and runtime.read_json(record)['status']!='running' and not runtime.locked(self.root/'control/runner.lock'):
                break
            time.sleep(0.05)
        else:
            runtime.atomic(self.root/'control/STOP',b'stop')
            self.fail('Background runner did not terminate in fixture budget')
        self.assertEqual(self.state()['status'],'completed')


if __name__=='__main__':
    unittest.main()
