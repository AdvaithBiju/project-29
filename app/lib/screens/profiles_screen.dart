import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/models.dart';
import '../services/api_service.dart';
import 'report_insights_screen.dart';

class ProfilesScreen extends StatefulWidget {
  const ProfilesScreen({super.key, required this.token, required this.onLogout});
  final String token;
  final VoidCallback onLogout;

  @override
  State<ProfilesScreen> createState() => _ProfilesScreenState();
}

class _ProfilesScreenState extends State<ProfilesScreen> {
  late ApiService _api;
  List<Profile> _profiles = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _api = ApiService('http://localhost:8000', widget.token);
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final data = await _api.fetchProfiles();
    setState(() {
      _profiles = data.map((p) => Profile.fromJson(p)).toList();
      _loading = false;
    });
  }

  Future<void> _createProfile() async {
    final nameController = TextEditingController();
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New profile'),
        content: TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Name')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
              onPressed: () async {
                await _api.createProfile({"name": nameController.text});
                if (context.mounted) Navigator.pop(context);
                _load();
              },
              child: const Text('Save')),
        ],
      ),
    );
  }

  Future<void> _upload(Profile profile) async {
    final result = await FilePicker.platform.pickFiles();
    if (result == null) return;
    final file = File(result.files.single.path!);
    final multipart = await http.MultipartFile.fromPath('file', file.path, filename: result.files.single.name);
    final report = await _api.uploadReport(profile.id, multipart);
    if (!mounted) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ReportInsightsScreen(
          token: widget.token,
          profileId: profile.id,
          reportId: report['id'],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profiles'),
        actions: [IconButton(onPressed: widget.onLogout, icon: const Icon(Icons.logout))],
      ),
      floatingActionButton: FloatingActionButton(onPressed: _createProfile, child: const Icon(Icons.add)),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _profiles.length,
              itemBuilder: (context, index) {
                final p = _profiles[index];
                return Card(
                  child: ListTile(
                    title: Text(p.name),
                    subtitle: Text('Sex: ${p.sex ?? 'N/A'} • Conditions: ${p.conditions.join(', ')}'),
                    trailing: IconButton(icon: const Icon(Icons.upload_file), onPressed: () => _upload(p)),
                    onTap: () => _upload(p),
                  ),
                );
              },
            ),
    );
  }
}
