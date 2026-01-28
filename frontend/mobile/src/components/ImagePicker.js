import * as ImagePicker from 'expo-image-picker';
import { Button } from 'react-native';

export default function ImagePickerComponent({ navigation }) {
  const pickImage = async () => {
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      base64: true
    });

    if (!result.canceled) {
      navigation.navigate('Result', { image: result.assets[0] });
    }
  };

  return <Button title="Capture Leaf Image" onPress={pickImage} />;
}
