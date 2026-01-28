import React from 'react';
import { View, Button, Text } from 'react-native';
import ImagePickerComponent from '../components/ImagePicker';

export default function HomeScreen({ navigation }) {
  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 22 }}>AI Crop Disease Detection</Text>
      <ImagePickerComponent navigation={navigation} />
    </View>
  );
}
