"""Karma Ecosystem — Web3 automation layer.

A complete automation system that connects Karma rewards for good deeds and
paid services to real blockchain hash transactions:

    Good deed / service  ->  on-chain reward (KARMA minted, tx hash)
    Subscription plans   ->  on-chain payments split to treasury (fee) +
                             protocol wallet, all enforced by smart contracts
    Treasury             ->  keeper automation pays coding agents
    Private vault        ->  AES-256-GCM encrypted document of all subscriber
                             account data created by the system

Run `python -m karma_ecosystem.cli --help` to see every command.
"""

__version__ = "1.0.0"
