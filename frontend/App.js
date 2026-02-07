import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Dimensions, TouchableOpacity, SafeAreaView, FlatList, Alert, Platform, Switch, Modal } from 'react-native';
import MapView, { Marker, Polyline, Callout } from 'react-native-maps';
import * as Location from 'expo-location';
import axios from 'axios';

// Replace with your machine's local IP address if running on device
const API_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';

export default function App() {
  const [location, setLocation] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [riskLevel, setRiskLevel] = useState('Unknown');
  const [sosActive, setSosActive] = useState(false);

  // Navigation State
  const [markers, setMarkers] = useState([]);
  const [routePath, setRoutePath] = useState([]);
  const [showNavControls, setShowNavControls] = useState(false);
  const [preferences, setPreferences] = useState({
    wheelchair: false,
    avoidCrowds: false,
    closestExit: false,
  });

  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setErrorMsg('Permission to access location was denied');
        return;
      }

      let loc = await Location.getCurrentPositionAsync({});
      setLocation(loc);
      pingLocation(loc.coords.latitude, loc.coords.longitude);
    })();

    fetchAlerts();
    fetchMarkers();
  }, []);

  const pingLocation = async (lat, lng) => {
    try {
      const res = await axios.post(`${API_URL}/ping-location`, {
        lat: lat, lng: lng, device_id: "mobile-user-123"
      });
      setRiskLevel(res.data.current_risk);
    } catch (err) { console.log("Ping failed:", err.message); }
  };

  const fetchAlerts = async () => {
    try {
      const res = await axios.get(`${API_URL}/live-alerts`);
      setAlerts(res.data);
    } catch (err) { console.log("Alerts failed:", err.message); }
  };

  const fetchMarkers = async () => {
    try {
      const res = await axios.get(`${API_URL}/markers`);
      setMarkers(res.data);
    } catch (err) { console.log("Markers failed:", err.message); }
  };

  const calculateRoute = async () => {
    if (!location) {
      Alert.alert("Location Missing", "Waiting for GPS...");
      return;
    }

    // Default destination (Main Stage for demo) if not "closest exit"
    // In a real app, user would select a marker as destination
    const DEMO_DEST = { lat: 30.2675, lng: -97.7690 }; // Stage Amex

    try {
      const res = await axios.post(`${API_URL}/safe-route`, {
        start_lat: location.coords.latitude,
        start_lng: location.coords.longitude,
        end_lat: preferences.closestExit ? null : DEMO_DEST.lat,
        end_lng: preferences.closestExit ? null : DEMO_DEST.lng,
        prefer_wheelchair: preferences.wheelchair,
        avoid_crowds: preferences.avoidCrowds,
        closest_exit: preferences.closestExit
      });

      const path = res.data.route.map(node => ({
        latitude: node.lat,
        longitude: node.lng
      }));

      if (path.length > 0) {
        setRoutePath(path);
        setShowNavControls(false); // Close modal
      } else {
        Alert.alert("No Route", "Could not find a safe path with these settings.");
      }

    } catch (err) {
      console.log("Route failed:", err.message);
      Alert.alert("Error", "Failed to calculate route.");
    }
  };

  const handleSOS = async () => {
    setSosActive(true);
    try {
      if (location) {
        await axios.post(`${API_URL}/sos`, {
          lat: location.coords.latitude,
          lng: location.coords.longitude,
          user_id: "mobile-user-123",
          message: "MOBILE SOS TRIGGERED"
        });
        Alert.alert("SOS SENT", "Emergency services notified.");
      }
    } catch (err) { setSosActive(false); }
  };

  const togglePref = (key) => {
    setPreferences(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>ACL 2026</Text>
        <TouchableOpacity onPress={() => setShowNavControls(true)} style={styles.navButton}>
          <Text style={styles.navButtonText}>Navigate</Text>
        </TouchableOpacity>
        <View style={[styles.riskBadge, riskLevel === 'High' ? styles.bgRed : riskLevel === 'Low' ? styles.bgGreen : styles.bgYellow]}>
          <Text style={styles.riskText}>{riskLevel}</Text>
        </View>
      </View>

      <View style={styles.mapContainer}>
        <MapView style={styles.map}
          initialRegion={{
            latitude: 30.2672, longitude: -97.7731,
            latitudeDelta: 0.015, longitudeDelta: 0.015,
          }}
          showsUserLocation={true}
        >
          {markers.map((marker, index) => (
            <Marker key={index} coordinate={{ latitude: marker.lat, longitude: marker.lng }}
              title={marker.type.toUpperCase()}
              pinColor={marker.type === 'medical' ? 'red' : marker.type === 'exit' ? 'green' : 'blue'}
            />
          ))}

          {routePath.length > 0 && (
            <Polyline coordinates={routePath} strokeColor="#3b82f6" strokeWidth={4} />
          )}
        </MapView>

        <TouchableOpacity style={[styles.sosButton, sosActive && styles.sosActive]} onPress={handleSOS} onLongPress={() => setSosActive(false)}>
          <Text style={styles.sosText}>{sosActive ? 'SOS!' : 'SOS'}</Text>
        </TouchableOpacity>
      </View>

      {/* Navigation Preferences Modal */}
      <Modal visible={showNavControls} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Route Preferences</Text>

            <View style={styles.prefRow}>
              <Text style={styles.prefLabel}>Wheelchair Accessible</Text>
              <Switch value={preferences.wheelchair} onValueChange={() => togglePref('wheelchair')} />
            </View>
            <View style={styles.prefRow}>
              <Text style={styles.prefLabel}>Avoid Crowds</Text>
              <Switch value={preferences.avoidCrowds} onValueChange={() => togglePref('avoidCrowds')} />
            </View>
            <View style={styles.prefRow}>
              <Text style={styles.prefLabel}>Go to Closest Exit</Text>
              <Switch value={preferences.closestExit} onValueChange={() => togglePref('closestExit')} />
            </View>

            <TouchableOpacity style={styles.calcButton} onPress={calculateRoute}>
              <Text style={styles.calcButtonText}>Find Safe Route</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeButton} onPress={() => setShowNavControls(false)}>
              <Text style={styles.closeButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      <View style={styles.infoContainer}>
        <Text style={styles.sectionTitle}>Live Updates</Text>
        <FlatList
          data={alerts}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <View style={styles.alertItem}>
              <Text style={styles.alertTitle}>{item.title}</Text>
              <Text style={styles.alertSnippet} numberOfLines={2}>{item.snippet}</Text>
            </View>
          )}
          ListEmptyComponent={<Text style={{ color: '#888' }}>No active alerts.</Text>}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#2d2d2d' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#fff' },
  navButton: { backgroundColor: '#3b82f6', padding: 8, borderRadius: 8 },
  navButtonText: { color: 'white', fontWeight: 'bold' },
  riskBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  bgRed: { backgroundColor: '#dc2626' }, bgGreen: { backgroundColor: '#16a34a' }, bgYellow: { backgroundColor: '#ca8a04' },
  riskText: { color: '#fff', fontWeight: 'bold' },
  mapContainer: { flex: 2, position: 'relative' },
  map: { width: Dimensions.get('window').width, height: '100%' },
  sosButton: { position: 'absolute', bottom: 20, right: 20, width: 70, height: 70, borderRadius: 35, backgroundColor: '#ef4444', justifyContent: 'center', alignItems: 'center', elevation: 5 },
  sosActive: { backgroundColor: '#991b1b' },
  sosText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  infoContainer: { flex: 1, padding: 16, backgroundColor: '#262626' },
  sectionTitle: { color: '#d4d4d4', fontSize: 16, fontWeight: 'bold', marginBottom: 8 },
  alertItem: { backgroundColor: '#404040', padding: 12, borderRadius: 8, marginBottom: 8 },
  alertTitle: { color: '#60a5fa', fontWeight: 'bold', marginBottom: 4 },
  alertSnippet: { color: '#a3a3a3', fontSize: 12 },
  // Modal Styles
  modalOverlay: { flex: 1, justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.7)' },
  modalContent: { margin: 20, backgroundColor: '#333', borderRadius: 20, padding: 25, elevation: 5 },
  modalTitle: { fontSize: 22, fontWeight: 'bold', color: 'white', marginBottom: 20, textAlign: 'center' },
  prefRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  prefLabel: { color: 'white', fontSize: 16 },
  calcButton: { backgroundColor: '#16a34a', padding: 15, borderRadius: 10, alignItems: 'center', marginTop: 10 },
  calcButtonText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  closeButton: { marginTop: 15, alignItems: 'center' },
  closeButtonText: { color: '#aaa', fontSize: 14 }
});
