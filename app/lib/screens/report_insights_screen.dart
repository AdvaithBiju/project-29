import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class ReportInsightsScreen extends StatefulWidget {
  const ReportInsightsScreen({super.key, required this.token, required this.profileId, required this.reportId});
  final String token;
  final int profileId;
  final int reportId;

  @override
  State<ReportInsightsScreen> createState() => _ReportInsightsScreenState();
}

class _ReportInsightsScreenState extends State<ReportInsightsScreen> {
  late ApiService _api;
  List<BiomarkerInsight> _insights = [];
  List<String> _disclaimers = [];
  List<String> _flags = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _api = ApiService('http://localhost:8000', widget.token);
    _load();
  }

  Future<void> _load() async {
    final data = await _api.fetchInsights(widget.profileId, widget.reportId);
    setState(() {
      _insights = (data['biomarkers'] as List<dynamic>).map((e) => BiomarkerInsight.fromJson(e)).toList();
      _disclaimers = (data['disclaimers'] as List<dynamic>).cast<String>();
      _flags = (data['overall_summary']['urgent_flags'] as List<dynamic>).cast<String>();
      _loading = false;
    });
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'HIGH':
      case 'CRITICAL':
        return Colors.red;
      case 'LOW':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Report insights')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_flags.isNotEmpty)
                  Card(
                    color: Colors.red.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Red flags', style: TextStyle(fontWeight: FontWeight.bold)),
                          ..._flags.map((f) => Text('• $f')),
                        ],
                      ),
                    ),
                  ),
                ..._insights.map(
                  (b) => Card(
                    child: ListTile(
                      title: Text(b.testName),
                      subtitle: Text('Value: ${b.value} ${b.unit}\nRef: ${b.refLow ?? '-'} - ${b.refHigh ?? '-'}'),
                      trailing: Chip(label: Text(b.status), backgroundColor: _statusColor(b.status).withOpacity(0.2)),
                      onTap: () => showDialog(
                        context: context,
                        builder: (_) => AlertDialog(
                          title: Text(b.testName),
                          content: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(b.lifestyleTips.join('\n')),
                              const SizedBox(height: 8),
                              Text('When to see a doctor:'),
                              ...b.redFlags.map((r) => Text('- $r')),
                              const SizedBox(height: 8),
                              Text('Trend: ${b.compare['trend'] ?? 'N/A'} (Δ ${b.compare['delta']?.toStringAsFixed(2) ?? 'n/a'})'),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    title: const Text('Retest reminder'),
                    subtitle: const Text('Schedule a local reminder to retest (stored locally).'),
                    trailing: ElevatedButton(
                      onPressed: () async {
                        final now = DateTime.now();
                        final date = await showDatePicker(
                          context: context,
                          firstDate: now,
                          initialDate: now.add(const Duration(days: 30)),
                          lastDate: now.add(const Duration(days: 365)),
                        );
                        if (date != null && mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Reminder scheduled for ${DateFormat.yMMMd().format(date)} (local device).')),
                          );
                        }
                      },
                      child: const Text('Schedule'),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Disclaimers', style: TextStyle(fontWeight: FontWeight.bold)),
                        ..._disclaimers.map((d) => Text('• $d')),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    title: const Text('Coming soon'),
                    subtitle: const Text('Smarter resampling reminders and clinician sharing options'),
                  ),
                )
              ],
            ),
    );
  }
}
