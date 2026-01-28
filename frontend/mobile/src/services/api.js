import axios from 'axios';

const API_URL = "http://YOUR_BACKEND_IP:8000";

export default {
  predict: async (image) => {
    const formData = new FormData();
    formData.append('file', {
      uri: image.uri,
      name: 'leaf.jpg',
      type: 'image/jpeg'
    });

    const res = await axios.post(`${API_URL}/detect`, formData);
    return res.data;
  }
};
