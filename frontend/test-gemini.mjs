// Test script for Gemini API using official SDK
import { GoogleGenerativeAI } from '@google/generative-ai';

const API_KEY = 'AIzaSyA_ENhOlws37iCEd9Trc8Mwoh6_UCKWfm4';
const genAI = new GoogleGenerativeAI(API_KEY);

async function main() {
    console.log('Testing Gemini API with official SDK...\n');

    try {
        const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

        console.log('Generating content...');
        const result = await model.generateContent('Generate 3 simple interview questions.');
        const response = await result.response;
        const text = response.text();

        console.log('\n✅ SUCCESS! Response:');
        console.log(text);
    } catch (error) {
        console.log('\n❌ ERROR:', error.message);
        if (error.message.includes('API_KEY')) {
            console.log('\nThe API key may be invalid or not enabled for Gemini API.');
            console.log('Please check: https://makersuite.google.com/app/apikey');
        }
    }
}

main();
