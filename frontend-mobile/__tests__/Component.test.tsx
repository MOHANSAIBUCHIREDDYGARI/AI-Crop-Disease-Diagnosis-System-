import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { View, Text } from 'react-native';

// A simple function to test
const sum = (a: number, b: number) => {
    return a + b;
};

describe('Basic Math Test', () => {
    it('adds 1 + 2 to equal 3', () => {
        expect(sum(1, 2)).toBe(3);
    });
});

const SimpleComponent = () => (
    <View>
        <Text>Hello, World!</Text>
    </View>
);

describe('<SimpleComponent />', () => {
    it('renders correctly', () => {
        render(<SimpleComponent />);
        expect(screen.getByText('Hello, World!')).toBeTruthy();
    });
});
