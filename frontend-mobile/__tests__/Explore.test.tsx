import React, { act } from 'react';
import renderer from 'react-test-renderer';
import ExploreScreen from '../app/(tabs)/explore'; // Adjust import based on file structure

// Mock Expo modules
jest.mock('expo-image-picker', () => ({
    launchImageLibraryAsync: jest.fn(),
}));

jest.mock('expo-router', () => ({
    useRouter: () => ({
        push: jest.fn(),
    }),
}));

// Mock Reanimated to avoid animation issues in tests
jest.mock('react-native-reanimated', () => {
    const Reanimated = require('react-native-reanimated/mock');
    Reanimated.default.call = () => { };
    return Reanimated;
});

// Mock ParallaxScrollView to simplify the test tree
jest.mock('@/components/parallax-scroll-view', () => {
    const { View } = require('react-native');
    return ({ children }: { children: React.ReactNode }) => <View>{children}</View>;
});

describe('<ExploreScreen />', () => {
    it('renders correctly', () => {
        let tree: renderer.ReactTestRenderer | undefined;
        act(() => {
            tree = renderer.create(<ExploreScreen />);
        });
        expect(tree).toBeDefined();
        if (tree) {
            expect(tree.toJSON()).toBeDefined();
        }
    });
});
