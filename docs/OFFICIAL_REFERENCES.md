# Official References

This repo keeps external protocol assumptions explicit. Reviewers should use the upstream references below when checking claims about Uniswap v4 behavior, deployment addresses, and hook mechanics.

## Uniswap V4

| Topic | Reference | Used for |
| --- | --- | --- |
| Hook concepts | https://developers.uniswap.org/contracts/v4/concepts/hooks | Hooks as pool-attached contracts, optional hook functions, and `afterSwap` lifecycle point. |
| Swap hooks | https://developers.uniswap.org/contracts/v4/quickstart/hooks/swap | Swap callback framing and `beforeSwap` / `afterSwap` behavior. |
| Hook deployment | https://developers.uniswap.org/docs/protocols/v4/guides/hooks/hook-deployment | Address-encoded permissions, hook flags, and address mining requirement. |
| Deployments | https://developers.uniswap.org/contracts/v4/deployments | Current PoolManager and periphery addresses by network. |
| PoolManager | https://developers.uniswap.org/contracts/v4/reference/core/interfaces/IPoolManager | Singleton PoolManager role in swaps, pools, and hooks. |

## Current Base Sepolia Assumption

Re-checked on May 19, 2026 against the official Uniswap v4 deployments page: Base Sepolia chain id `84532` lists PoolManager:

```text
0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408
```

Any live release record must re-check this upstream page before deployment. Deployment addresses can change across protocol versions and networks; the public release should never rely on stale copied constants.

## Hook Flag Assumption

The public hook planner targets the `afterSwap` flag only:

```text
AFTER_SWAP_FLAG = 1 << 6 = 0x40
```

This follows Uniswap v4's address-encoded hook permission model. The hook address must be mined so its low hook bits represent exactly the intended permissions.
