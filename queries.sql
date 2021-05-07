-- Annual rainfall averages from daily
SELECT date_trunc('year', timestamp)::date as dt, min(timestamp) as earliest, max(timestamp) as latest, sum(value), round(364*sum(value)/extract(day from max(timestamp)-min(timestamp))) from observation where dataset='climat0900' and variable='Rain_accum_0909' group by dt order by dt desc limit 60;

-- Daily rainfall summed from hourly
SELECT date_trunc('day', timestamp)::date as dt, max(timestamp), min(timestamp), sum(value)::numeric from observation where dataset='1hour_Level2' and variable='Rain' group by dt order by dt desc limit 20;
