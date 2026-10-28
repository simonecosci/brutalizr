interface ReportRow {
  label: string;
  value: number;
}

type ChartKind = 'bar' | 'line';

enum ExportFormat { Csv, Pdf }

export class ReportService {
  private readonly cache = new Map<string, ReportRow[]>();

  constructor(private baseUrl: string) {}

  buildReport(title: string, rows: ReportRow[], kind: ChartKind = 'bar'): string {
    const totalValue = rows.reduce((sum, row) => sum + row.value, 0);
    this.cache.set(title, rows);
    return `${title} [${kind}] total=${totalValue} @ ${this.baseUrl} as ${ExportFormat[ExportFormat.Csv]}`;
  }
}

const reportService = new ReportService('https://api.example.com');
const sampleRows: ReportRow[] = [{ label: 'a', value: 1 }, { label: 'b', value: 2 }];
console.log(reportService.buildReport('Vendite', sampleRows));
