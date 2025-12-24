import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/auth_screen.dart';
import 'screens/profiles_screen.dart';

void main() {
  runApp(const BloodReportApp());
}

class BloodReportApp extends StatefulWidget {
  const BloodReportApp({super.key});

  @override
  State<BloodReportApp> createState() => _BloodReportAppState();
}

class _BloodReportAppState extends State<BloodReportApp> {
  String? _token;

  @override
  void initState() {
    super.initState();
    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _token = prefs.getString('jwt');
    });
  }

  void _onLogin(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt', token);
    setState(() {
      _token = token;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blood Report Analyzer',
      theme: ThemeData(primarySwatch: Colors.red),
      home: _token == null
          ? AuthScreen(onLogin: _onLogin)
          : ProfilesScreen(token: _token!, onLogout: () async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.remove('jwt');
              setState(() {
                _token = null;
              });
            }),
    );
  }
}
