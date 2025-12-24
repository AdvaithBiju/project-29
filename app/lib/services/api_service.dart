import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  ApiService(this.baseUrl, this.token);
  final String baseUrl;
  String? token;

  Map<String, String> _headers() => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<String> login(String email, String password) async {
    final res = await http.post(Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}));
    if (res.statusCode != 200) throw Exception('Login failed');
    final data = jsonDecode(res.body);
    token = data['access_token'];
    return token!;
  }

  Future<void> register(String email, String password) async {
    final res = await http.post(Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}));
    if (res.statusCode != 200) throw Exception('Register failed');
  }

  Future<List<dynamic>> fetchProfiles() async {
    final res = await http.get(Uri.parse('$baseUrl/profiles'), headers: _headers());
    if (res.statusCode != 200) throw Exception('Failed to load profiles');
    return jsonDecode(res.body) as List<dynamic>;
  }

  Future<Map<String, dynamic>> createProfile(Map<String, dynamic> payload) async {
    final res = await http.post(Uri.parse('$baseUrl/profiles'), headers: _headers(), body: jsonEncode(payload));
    if (res.statusCode != 200) throw Exception('Failed to create profile');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> uploadReport(int profileId, http.MultipartFile file) async {
    final uri = Uri.parse('$baseUrl/profiles/$profileId/reports');
    final request = http.MultipartRequest('POST', uri)
      ..headers.addAll({if (token != null) 'Authorization': 'Bearer $token'})
      ..files.add(file);
    final streamed = await request.send();
    final res = await http.Response.fromStream(streamed);
    if (res.statusCode != 200) throw Exception('Upload failed');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> fetchInsights(int profileId, int reportId) async {
    final res = await http.get(Uri.parse('$baseUrl/profiles/$profileId/reports/$reportId/insights'), headers: _headers());
    if (res.statusCode != 200) throw Exception('Failed to load insights');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
