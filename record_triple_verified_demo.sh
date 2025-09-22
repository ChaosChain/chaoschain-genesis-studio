#!/bin/bash
# 🎬 ChaosChain SDK Triple-Verified Stack Demo
# Clean recording script for professional video

echo "🎬 ChaosChain SDK Triple-Verified Stack Demo"
echo "============================================="
echo ""
echo "🎯 This demo shows:"
echo "  • Server agent with process integrity"
echo "  • Client agent executing Triple-Verified Stack"
echo "  • Real blockchain transactions and IPFS proofs"
echo ""
echo "📋 Recording Tips:"
echo "  • Use full screen terminal"
echo "  • Font size 14+ for readability"
echo "  • Demo runs automatically (no user input)"
echo ""

read -p "🎥 Ready to start? Press ENTER..."

# Clear screen for clean start
clear

# Set environment variables
export BASE_SEPOLIA_RPC_URL='https://sepolia.base.org'

# Run the Triple-Verified Stack demo
python3 triple_verified_demo.py

echo ""
echo "🎬 Demo complete! Perfect for your launch video."
