# Security Definer Views Remediation

## 🚨 Security Issue Summary

Your Supabase database contains three views that use the `SECURITY DEFINER` property, which is flagged as a security vulnerability:

1. `public.system_health`
2. `public.portfolio_summary` 
3. `public.recent_insights`

## ⚠️ What is SECURITY DEFINER?

The `SECURITY DEFINER` property on database views means:
- The view executes with the privileges of the **view creator** (definer)
- Not with the privileges of the **user querying the view** (invoker)
- This can bypass Row Level Security (RLS) policies
- It can potentially allow unauthorized access to data

## 🔧 The Fix

I've created secure replacement views that:
- ✅ Remove the `SECURITY DEFINER` property
- ✅ Work with your existing RLS policies
- ✅ Maintain the same functionality
- ✅ Follow security best practices

## 📋 How to Apply the Fix

### Option 1: Using Supabase Dashboard (Recommended)

1. **Open your Supabase dashboard**
2. **Navigate to SQL Editor**
3. **Copy and paste the contents** of `api/database/fix_security_definer_views.sql`
4. **Run the SQL script**
5. **Verify the views are working** by testing queries

### Option 2: Using CLI

```bash
# If you have Supabase CLI installed
supabase db reset --linked
# Then run the new schema
```

### Option 3: Manual Database Connection

```bash
# Connect to your Supabase database directly
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run the SQL file
\i api/database/fix_security_definer_views.sql
```

## 🔍 What Each View Does

### `system_health`
- **Purpose**: Provides system health metrics
- **Data**: Active metrics, response times, recent insights/events
- **Security**: Now respects RLS policies from base tables

### `portfolio_summary`
- **Purpose**: Overview of portfolio analysis metrics
- **Data**: Portfolio size, risk levels, high-impact counts
- **Security**: Now respects RLS policies from base tables

### `recent_insights`
- **Purpose**: Recent insights with contextual metadata
- **Data**: Latest insights, confidence scores, time-based context
- **Security**: Now respects RLS policies from base tables

## 🧪 Testing the Fix

After applying the fix, test each view:

```sql
-- Test system_health view
SELECT * FROM public.system_health;

-- Test portfolio_summary view
SELECT * FROM public.portfolio_summary;

-- Test recent_insights view
SELECT * FROM public.recent_insights LIMIT 10;
```

## 🛡️ Security Benefits

1. **RLS Compliance**: Views now inherit security from base tables
2. **Proper Permissions**: Explicit grants to `authenticated` and `service_role`
3. **No Privilege Escalation**: Users can only see data they're authorized to access
4. **Audit Trail**: Clear documentation of security changes

## 📚 Best Practices Moving Forward

1. **Never use SECURITY DEFINER** unless absolutely necessary
2. **Use RLS policies** on base tables instead
3. **Grant explicit permissions** to roles
4. **Document security decisions** in comments
5. **Test views** with different user roles

## 🔄 Rollback Plan

If you need to rollback (not recommended):

```sql
-- Only if absolutely necessary
DROP VIEW IF EXISTS public.system_health;
DROP VIEW IF EXISTS public.portfolio_summary;
DROP VIEW IF EXISTS public.recent_insights;

-- Then recreate with SECURITY DEFINER (NOT RECOMMENDED)
-- You would need to get the original view definitions
```

## 🎯 Next Steps

1. **Apply the fix** using one of the methods above
2. **Test your application** to ensure everything works
3. **Monitor the database** for any performance issues
4. **Update your application code** if needed (unlikely)
5. **Run the Supabase linter again** to verify the warnings are gone

## 📞 Support

If you encounter issues:
1. Check the Supabase logs for errors
2. Verify RLS policies are working correctly
3. Test with both `authenticated` and `service_role` users
4. Review the view definitions for any typos

The new views are designed to be drop-in replacements, so your existing application code should continue to work without changes. 