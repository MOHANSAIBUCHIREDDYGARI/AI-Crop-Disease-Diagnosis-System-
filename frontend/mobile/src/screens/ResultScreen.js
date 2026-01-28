import React, { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import api from '../services/api';

export default function ResultScreen({ route }) {
  const { image } = route.params;
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.predict(image).then(setResult);
  }, []);

  if (!result) return <Text>Analyzing...</Text>;

  return (
    <View>
      <Text>Crop: {result.crop}</Text>
      <Text>Disease: {result.disease}</Text>
      <Text>Confidence: {result.confidence}%</Text>
      <Text>Stage: {result.stage}</Text>
    </View>
  );
}
