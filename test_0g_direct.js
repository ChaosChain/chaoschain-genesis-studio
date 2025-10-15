const { createZGComputeNetworkBroker } = require('@0glabs/0g-serving-broker');
const { ethers } = require('ethers');

async function test() {
    try {
        const provider = new ethers.JsonRpcProvider('https://evmrpc-testnet.0g.ai');
        const wallet = new ethers.Wallet('0xd5e6046419db99358ec9b10e11a398989b8e5432fe0e2b4174a094063d05ea42', provider);
        
        console.log('1. Creating broker...');
        const broker = await createZGComputeNetworkBroker(wallet);
        console.log('✅ Broker created');
        
        console.log('2. Checking balance...');
        const account = await broker.ledger.getLedger();
        console.log(`✅ Balance: ${ethers.formatEther(account.totalBalance)} OG`);
        
        if (account.totalBalance < ethers.parseEther('0.1')) {
            console.log('3. Adding funds...');
            await broker.ledger.addLedger(1);
            console.log('✅ Funds added');
        }
        
        const providerAddress = '0xf07240Efa67755B5311bc75784a061eDB47165Dd';
        
        console.log('4. Acknowledging provider...');
        await broker.inference.acknowledgeProviderSigner(providerAddress);
        console.log('✅ Provider acknowledged');
        
        console.log('5. Getting metadata...');
        const { endpoint, model } = await broker.inference.getServiceMetadata(providerAddress);
        console.log(`✅ Endpoint: ${endpoint}, Model: ${model}`);
        
        console.log('6. Generating headers...');
        const messages = [{ role: 'user', content: 'Say hello' }];
        const headers = await broker.inference.getRequestHeaders(providerAddress, JSON.stringify(messages));
        console.log('✅ Headers generated');
        
        console.log('7. Making inference request...');
        const response = await fetch(`${endpoint}/chat/completions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...headers },
            body: JSON.stringify({ messages, model })
        });
        
        console.log(`Response status: ${response.status}`);
        const text = await response.text();
        console.log(`Response text: ${text.substring(0, 200)}`);
        
        if (response.ok) {
            const data = JSON.parse(text);
            console.log('✅ SUCCESS!');
            console.log(`ChatID: ${data.id}`);
            console.log(`Answer: ${data.choices[0].message.content}`);
        } else {
            console.log('❌ API Error:', text);
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.error('Stack:', error.stack);
    }
}

test();
