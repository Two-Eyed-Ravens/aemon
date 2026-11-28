import { useEffect, useState } from 'react';
import { api, errorText } from '../api.ts';
import { RunView } from '../components/Run.tsx';
import type { RunRecord } from '../types.ts';

type Arm = 'baseline' | 'candidate';
interface Metrics { episodes: number; finished: number; guards_cleared: number; prompt_tokens: number; completion_tokens: number }
interface Episode { arm: Arm; finished: boolean; guards_cleared: boolean; stop_reason: string; prompt_tokens: number; completion_tokens: number; record: RunRecord }
interface Pair { case: string; attempt: number; baseline: Episode | null; candidate: Episode | null }
interface Experiment {
  id: string;
  state: 'pending' | 'incomplete' | 'complete' | 'invalid';
  baseline: Record<string, unknown> | null;
  candidate: Record<string, unknown> | null;
  protocol: Record<string, unknown> | null;
  selection: Record<string, unknown> | null;
  manifest: Record<string, unknown> | null;
  issues: string[];
  metrics: Record<Arm, Metrics | null>;
  pairs: Pair[];
}
const ARMS: Arm[] = ['baseline', 'candidate'];
const label = (arm: Arm): string => arm === 'baseline' ? 'Baseline' : 'Candidate';

function ArmResult({ episode, arm, runKey }: { episode: Episode | null; arm: Arm; runKey: string }) {
  return <section className="panel pad cmp-col">
    <h3>{label(arm)}</h3>
    {episode ? <>
      <p>{episode.finished ? 'Finished' : 'Not finished'} · {episode.guards_cleared ? 'Mechanical guards cleared' : 'Mechanical guards not cleared'}</p>
      <p className="small muted">Stop: {episode.stop_reason} · Prompt tokens: {episode.prompt_tokens} · Completion tokens: {episode.completion_tokens}</p>
      {episode.record.final?.recommendation ? <p>{episode.record.final.recommendation}</p> : <p className="muted">No final recommendation recorded.</p>}
      <RunView key={runKey} record={episode.record} runKey={runKey} />
    </> : <p className="muted">This arm has no recorded result.</p>}
  </section>;
}

function Campaign({ experiment: e }: { experiment: Experiment }) {
  const [selected, setSelected] = useState('');
  const pair = e.pairs.find((p) => `${p.case}:${p.attempt}` === selected) ?? e.pairs[0];
  const title = typeof e.candidate?.name === 'string' ? e.candidate.name : e.id;
  return <article className="panel pad cmp-col">
    <header className="row spread"><h2>{title}</h2><span className={`chip ${e.state === 'invalid' ? 'bad' : 'warn'}`}>{e.state}</span></header>
    <p className="small muted">{e.id}</p>
    {e.state === 'pending' ? <p>Registered; no campaign results recorded.</p> : null}
    {e.state === 'incomplete' ? <p>Partial evidence. Execution has not been confirmed complete.</p> : null}
    {e.issues.map((issue, i) => <p key={i} role="status">{issue}</p>)}
    <div className="cmp-grid">{ARMS.map((arm) => {
      const m = e.metrics[arm];
      return <section key={arm}><h3>{label(arm)}</h3>{m ? <dl className="cmp-dl">
        <div><dt>Observed episodes</dt><dd>{m.episodes}</dd></div>
        <div><dt>Finished</dt><dd>{m.finished} / {m.episodes}</dd></div>
        <div><dt>Mechanical guards cleared</dt><dd>{m.guards_cleared} / {m.episodes}</dd></div>
        <div><dt>Prompt / completion tokens</dt><dd>{m.prompt_tokens} / {m.completion_tokens}</dd></div>
      </dl> : <p className="muted">No valid results recorded.</p>}</section>;
    })}</div>
    <p><b>Independent blind quality review: pending.</b> Mechanical checks do not establish strategic quality. No policy is automatically accepted or activated.</p>
    <details><summary>Protocol, configuration and provisional selection</summary><pre className="small">{JSON.stringify({ baseline: e.baseline, candidate: e.candidate, protocol: e.protocol, selection: e.selection, manifest: e.manifest }, null, 2)}</pre></details>
    {pair ? <>
      <label>Case and attempt <select value={`${pair.case}:${pair.attempt}`} onChange={(event) => setSelected(event.target.value)}>
        {e.pairs.map((p) => <option key={`${p.case}:${p.attempt}`} value={`${p.case}:${p.attempt}`}>{p.case} · attempt {p.attempt}</option>)}
      </select></label>
      <div className="cmp-grid">{ARMS.map((arm) => <ArmResult key={arm} arm={arm} episode={pair[arm]} runKey={`${e.id}:${pair.case}:${pair.attempt}:${arm}`} />)}</div>
    </> : null}
  </article>;
}

export function HarnessPage() {
  const [experiments, setExperiments] = useState<Experiment[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError(null);
    api<{ experiments: Experiment[] }>('/api/harness/experiments').then((response) => {
      if (alive) setExperiments(response.experiments);
    }).catch((failure: unknown) => { if (alive) setError(errorText(failure)); }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [revision]);
  return <div className="pg cmp">
    <header className="pg-head"><div><h1 className="pg-title">Harness experiments</h1><p className="pg-sub">Recorded offline experiments with paired baseline and candidate traces. Counts describe observed runs; they are not quality scores.</p></div>
      <button type="button" className="button" disabled={loading} onClick={() => setRevision(revision + 1)}>{loading ? 'Loading…' : 'Refresh'}</button>
    </header>
    {error ? <p role="alert">Could not load experiments: {error}. {experiments ? 'Previously loaded results remain below.' : 'Use Refresh to retry.'}</p> : null}
    {!loading && !error && !experiments?.length ? <p>No experiments registered.</p> : null}
    {experiments?.map((experiment) => <Campaign key={experiment.id} experiment={experiment} />)}
  </div>;
}
