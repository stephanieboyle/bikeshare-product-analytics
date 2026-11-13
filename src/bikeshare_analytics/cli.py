import argparse
import logging


def main():
    p = argparse.ArgumentParser(description='Independent bike-share product analytics')
    sub = p.add_subparsers(dest='command', required=True)
    h = sub.add_parser('history')
    h.add_argument('--months', nargs='+', default=['202608', '202609', '202610'])
    h.add_argument('--limit', type=int, help='First N rows/month: feasibility only, not representative')
    h.add_argument('--db', default='data/bikeshare.duckdb')
    c = sub.add_parser('collect')
    c.add_argument('--count', type=int, default=1)
    c.add_argument('--interval', type=int, default=120)
    c.add_argument('--db', default='data/bikeshare.duckdb')
    r = sub.add_parser('report')
    r.add_argument('--db', default='data/bikeshare.duckdb')
    s = sub.add_parser('simulate')
    s.add_argument('--repetitions', type=int, default=2000)
    s.add_argument('--users', type=int, default=4000, help='Per arm')
    s.add_argument('--seed', type=int, default=20261113)
    a = p.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    if a.command == 'history':
        from .history import ingest
        ingest(a.months, a.db, a.limit)
    elif a.command == 'collect':
        from .collect import collect
        collect(a.db, a.count, a.interval)
    elif a.command == 'report':
        from .report import report
        report(a.db)
    else:
        from .simulation import simulate
        simulate(a.repetitions, a.users, a.seed)


if __name__ == '__main__':
    main()
