#!/bin/bash
# 🎬 ChaosChain SDK Demo Recording Script
# Perfect for creating a professional demo video

echo "🎬 ChaosChain SDK Demo Recording Setup"
echo "======================================"
echo ""
echo "📋 Pre-Recording Checklist:"
echo "  ✅ Terminal window sized appropriately"
echo "  ✅ Font size readable for video"
echo "  ✅ Screen recording software ready"
echo "  ✅ Audio recording ready (optional)"
echo ""
echo "🎯 Demo Flow (60 seconds):"
echo "  0-10s:  Installation command"
echo "  10-25s: Agent creation (3 lines of code)"
echo "  25-35s: Identity registration on blockchain"
echo "  35-45s: Payment methods and integrations"
echo "  45-55s: SDK status and capabilities"
echo "  55-60s: Conclusion with key benefits"
echo ""
echo "🔥 Key Talking Points:"
echo "  • Zero setup - just pip install"
echo "  • Triple-Verified Stack"
echo "  • Real blockchain integration"
echo "  • 5 payment methods including crypto"
echo "  • Production ready"
echo ""

read -p "🎥 Ready to start demo? Press ENTER to begin..."

# Clear screen for clean start
clear

# Set environment variables
export BASE_SEPOLIA_RPC_URL='https://sepolia.base.org'

# Run the demo
echo "🚀 Starting ChaosChain SDK Demo..."
echo ""
python3 demo_script.py

echo ""
echo "🎬 Demo complete! Perfect for your video."
echo ""
echo "📝 Next Steps:"
echo "  1. Edit the video to highlight key moments"
echo "  2. Add voice-over explaining the Triple-Verified Stack"
echo "  3. Include links to docs.chaoscha.in and PyPI"
echo "  4. Share with the developer community!"
